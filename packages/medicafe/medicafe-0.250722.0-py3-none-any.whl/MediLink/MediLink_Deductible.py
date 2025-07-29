"""
# Create a summary JSON
summary = {
    "Payer ID": ins_payerID,
    "Provider": provider_last_name,
    "Member ID": ins_memberID,
    "Date of Birth": dob,
    "Patient Name": patient_name,
    "Patient Info": {
        "DOB": dob,
        "Address": "{} {}".format(patient_info.get("addressLine1", ""), patient_info.get("addressLine2", "")).strip(),
        "City": patient_info.get("city", ""),
        "State": patient_info.get("state", ""),
        "ZIP": patient_info.get("zip", ""),
        "Relationship": patient_info.get("relationship", "")
    },
    "Insurance Info": {
        "Payer Name": insurance_info.get("payerName", ""),
        "Payer ID": ins_payerID,
        "Member ID": ins_memberID,
        "Group Number": insurance_info.get("groupNumber", ""),
        "Insurance Type": ins_insuranceType,
        "Type Code": ins_insuranceTypeCode,
        "Address": "{} {}".format(insurance_info.get("addressLine1", ""), insurance_info.get("addressLine2", "")).strip(),
        "City": insurance_info.get("city", ""),
        "State": insurance_info.get("state", ""),
        "ZIP": insurance_info.get("zip", "")
    },
    "Policy Info": {
        "Eligibility Dates": eligibilityDates,
        "Policy Member ID": policy_info.get("memberId", ""),
        "Policy Status": policy_status
    },
    "Deductible Info": {
        "Remaining Amount": remaining_amount
    }
}

Features Added:
1. Allows users to manually input patient information for deductible lookup before processing CSV data.
2. Supports multiple manual requests, each generating its own Notepad file.
3. Validates user inputs and provides feedback on required formats.
4. Displays available Payer IDs as a note after manual entries.
"""
# MediLink_Deductible.py
import MediLink_API_v3
import os, sys, requests, json
from datetime import datetime

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

try:
    from MediLink import MediLink_Deductible_Validator
except ImportError:
    import MediLink_Deductible_Validator

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)

try:
    from MediBot import MediBot_Preprocessor_lib
except ImportError:
    import MediBot_Preprocessor_lib

# Function to check if the date format is correct
def validate_and_format_date(date_str):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%d-%m-%Y'):
        try:
            formatted_date = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            continue
    return None

# Load configuration
config, _ = MediLink_ConfigLoader.load_configuration()

# Initialize the API client
client = MediLink_API_v3.APIClient()

# Get provider_last_name and npi from configuration
provider_last_name = config['MediLink_Config'].get('default_billing_provider_last_name', 'Unknown')
npi = config['MediLink_Config'].get('default_billing_provider_npi', 'Unknown')

# Check if the provider_last_name is still 'Unknown'
if provider_last_name == 'Unknown':
    MediLink_ConfigLoader.log("Warning: provider_last_name was not found in the configuration.", level="WARNING")

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '06111', '37602']  # United Healthcare.

# Get the latest CSV
CSV_FILE_PATH = config.get('CSV_FILE_PATH', "")
csv_data = MediBot_Preprocessor_lib.load_csv_data(CSV_FILE_PATH)

# Only keep rows that contain a valid number from the payer_ids list
valid_rows = [row for row in csv_data if str(row.get('Ins1 Payer ID', '')) in payer_ids]

# Extract important columns for summary with fallback
summary_valid_rows = [
    {
        'DOB': row.get('Patient DOB', row.get('DOB', '')),  # Try 'Patient DOB' first, then 'DOB'
        'Ins1 Member ID': row.get('Primary Policy Number', row.get('Ins1 Member ID', '')),  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
        'Ins1 Payer ID': row.get('Ins1 Payer ID', '')
    }
    for row in valid_rows
]

# Print summary of valid rows
print("\n--- Summary of Valid Rows ---")
for row in summary_valid_rows:
    print("DOB: {}, Member ID: {}, Payer ID: {}".format(row['DOB'], row['Ins1 Member ID'], row['Ins1 Payer ID']))

# List of patients with DOB and MemberID from CSV data with fallback
patients = [
    (validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))),  # Try 'Patient DOB' first, then 'DOB'
     row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip())  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
    for row in valid_rows 
    if validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))) is not None and 
       row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip()
]

# Function to handle manual patient deductible lookup
def manual_deductible_lookup():
    print("\n--- Manual Patient Deductible Lookup ---")
    print("Available Payer IDs: {}".format(", ".join(payer_ids)))
    print("Enter 'quit' at any time to return to main menu.\n")
    
    while True:
        member_id = input("Enter the Member ID of the subscriber (or 'quit' to exit): ").strip()
        if member_id.lower() == 'quit':
            print("Returning to main menu.\n")
            break
        if not member_id:
            print("No Member ID entered. Please try again.\n")
            continue

        dob_input = input("Enter the Date of Birth (YYYY-MM-DD): ").strip()
        if dob_input.lower() == 'quit':
            print("Returning to main menu.\n")
            break
            
        formatted_dob = validate_and_format_date(dob_input)
        if not formatted_dob:
            print("Invalid DOB format. Please enter in YYYY-MM-DD format.\n")
            continue

        print("\nProcessing manual lookup for Member ID: {}, DOB: {}".format(member_id, formatted_dob))
        print("Checking {} payer IDs...".format(len(payer_ids)))

        # Fetch eligibility data
        found_data = False
        for i, payer_id in enumerate(payer_ids, 1):
            print("Checking Payer ID {} ({}/{}): {}".format(payer_id, i, len(payer_ids), payer_id))
            
            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, formatted_dob, member_id, npi, run_validation=True)
            if eligibility_data:
                found_data = True
                # Generate unique output file for manual request
                output_file_name = "eligibility_report_manual_{}_{}.txt".format(member_id, formatted_dob)
                output_file_path = os.path.join(os.getenv('TEMP'), output_file_name)
                with open(output_file_path, 'w') as output_file:
                    table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                        "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
                    output_file.write(table_header + "\n")
                    output_file.write("-" * len(table_header) + "\n")
                    print(table_header)
                    print("-" * len(table_header))
                    display_eligibility_info(eligibility_data, formatted_dob, member_id, output_file)
                
                # Ask if user wants to open the report
                open_report = input("\nEligibility data found! Open the report? (Y/N): ").strip().lower()
                if open_report in ['y', 'yes']:
                    os.system('notepad.exe "{}"'.format(output_file_path))
                print("Manual eligibility report generated: {}\n".format(output_file_path))
                break  # Assuming one payer ID per manual lookup
            else:
                print("No eligibility data found for Payer ID: {}".format(payer_id))
        
        if not found_data:
            print("\nNo eligibility data found for any Payer ID.")
        
        # Ask if the user wants to perform another manual lookup
        continue_choice = input("\nDo you want to perform another manual lookup? (Y/N): ").strip().lower()
        if continue_choice in ['n', 'no']:
            break


# Function to get eligibility information
def get_eligibility_info(client, payer_id, provider_last_name, date_of_birth, member_id, npi, run_validation=False):
    try:
        # Log the parameters being sent to the function
        MediLink_ConfigLoader.log("Calling eligibility check with parameters:", level="DEBUG")
        MediLink_ConfigLoader.log("payer_id: {}".format(payer_id), level="DEBUG")
        MediLink_ConfigLoader.log("provider_last_name: {}".format(provider_last_name), level="DEBUG")
        MediLink_ConfigLoader.log("date_of_birth: {}".format(date_of_birth), level="DEBUG")
        MediLink_ConfigLoader.log("member_id: {}".format(member_id), level="DEBUG")
        MediLink_ConfigLoader.log("npi: {}".format(npi), level="DEBUG")

        # Configuration flag to control which API to use
        # Set to False to use the new Super Connector API, True to use the legacy v3 API
        USE_LEGACY_API = True  # Changed to True to use legacy as primary
        
        # Always get legacy response first
        MediLink_ConfigLoader.log("Getting legacy get_eligibility_v3 API response", level="INFO")
        legacy_eligibility = MediLink_API_v3.get_eligibility_v3(
            client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
        )
        
        # Also get Super Connector response for comparison
        MediLink_ConfigLoader.log("Getting new get_eligibility_super_connector API response", level="INFO")
        super_connector_eligibility = None
        try:
            super_connector_eligibility = MediLink_API_v3.get_eligibility_super_connector(
                client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
            )
        except Exception as e:
            MediLink_ConfigLoader.log("Super Connector API failed: {}".format(e), level="ERROR")
        
        # Run validation if requested and we have both responses
        if run_validation and legacy_eligibility and super_connector_eligibility:
            validation_file_path = os.path.join(os.getenv('TEMP'), 'validation_report_{}_{}.txt'.format(member_id, date_of_birth))
            validation_report = MediLink_Deductible_Validator.run_validation_comparison(
                legacy_eligibility, super_connector_eligibility, validation_file_path
            )
            print("\nValidation report generated: {}".format(validation_file_path))
            
                    # Log any Super Connector API errors
        if super_connector_eligibility and "rawGraphQLResponse" in super_connector_eligibility:
            raw_response = super_connector_eligibility.get('rawGraphQLResponse', {})
            errors = raw_response.get('errors', [])
            if errors:
                print("Super Connector API returned {} error(s):".format(len(errors)))
                for i, error in enumerate(errors):
                    error_code = error.get('code', 'UNKNOWN')
                    error_desc = error.get('description', 'No description')
                    print("  Error {}: {} - {}".format(i+1, error_code, error_desc))
                    
                    # Check for data in error extensions (some APIs return data here)
                    extensions = error.get('extensions', {})
                    if extensions and 'details' in extensions:
                        details = extensions.get('details', [])
                        if details:
                            print("    Found {} detail records in error extensions".format(len(details)))
                            # Log first detail record for debugging
                            if details:
                                first_detail = details[0]
                                print("    First detail: {}".format(first_detail))
            
            # Check status code
            status_code = super_connector_eligibility.get('statuscode')
            if status_code and status_code != '200':
                print("Super Connector API status code: {} (non-200 indicates errors)".format(status_code))
            
            # Open validation report in Notepad
            os.system('notepad.exe "{}"'.format(validation_file_path))
        
        # Return the primary response (legacy for now)
        eligibility = legacy_eligibility if USE_LEGACY_API else super_connector_eligibility
        
        # Log the response
        MediLink_ConfigLoader.log("Eligibility response: {}".format(json.dumps(eligibility, indent=4)), level="DEBUG")
        
        return eligibility
    except requests.exceptions.HTTPError as e:
        # Log the HTTP error response
        MediLink_ConfigLoader.log("HTTPError: {}".format(e), level="ERROR")
        MediLink_ConfigLoader.log("Response content: {}".format(e.response.content), level="ERROR")
    except Exception as e:
        # Log any other exceptions
        MediLink_ConfigLoader.log("Error: {}".format(e), level="ERROR")
    return None

# Helper functions to extract data from different API response formats
# BUG the API response is coming through correctly but the parsers below are not correctly extracting the super_connector variables.

def extract_legacy_patient_info(policy):
    """Extract patient information from legacy API response format"""
    patient_info = policy.get("patientInfo", [{}])[0]
    return {
        'lastName': patient_info.get("lastName", ""),
        'firstName': patient_info.get("firstName", ""),
        'middleName': patient_info.get("middleName", "")
    }

def extract_super_connector_patient_info(eligibility_data):
    """Extract patient information from Super Connector API response format"""
    if not eligibility_data:
        return {'lastName': '', 'firstName': '', 'middleName': ''}
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            member_info = first_eligibility.get('eligibilityInfo', {}).get('member', {})
            if member_info:
                return {
                    'lastName': member_info.get("lastName", ""),
                    'firstName': member_info.get("firstName", ""),
                    'middleName': member_info.get("middleName", "")
                }
        
        # Check for data in error extensions (some APIs return data here despite errors)
        errors = raw_response.get('errors', [])
        for error in errors:
            extensions = error.get('extensions', {})
            if extensions and 'details' in extensions:
                details = extensions.get('details', [])
                if details:
                    # Use the first detail record that has patient info
                    for detail in details:
                        if detail.get('lastName') or detail.get('firstName'):
                            return {
                                'lastName': detail.get("lastName", ""),
                                'firstName': detail.get("firstName", ""),
                                'middleName': detail.get("middleName", "")
                            }
    
    # Fallback to top-level fields
    return {
        'lastName': eligibility_data.get("lastName", ""),
        'firstName': eligibility_data.get("firstName", ""),
        'middleName': eligibility_data.get("middleName", "")
    }

def extract_legacy_remaining_amount(policy):
    """Extract remaining amount from legacy API response format"""
    deductible_info = policy.get("deductibleInfo", {})
    if 'individual' in deductible_info:
        remaining = deductible_info['individual']['inNetwork'].get("remainingAmount", "")
        return remaining if remaining else "Not Found"
    elif 'family' in deductible_info:
        remaining = deductible_info['family']['inNetwork'].get("remainingAmount", "")
        return remaining if remaining else "Not Found"
    else:
        return "Not Found"

def extract_super_connector_remaining_amount(eligibility_data):
    """Extract remaining amount from Super Connector API response format"""
    if not eligibility_data:
        return "Not Found"
    
    # First, check top-level metYearToDateAmount which might indicate deductible met
    met_amount = eligibility_data.get('metYearToDateAmount')
    if met_amount is not None:
        return str(met_amount)
    
    # Collect all deductible amounts to find the most relevant one
    all_deductible_amounts = []
    
    # Look for deductible information in planLevels (based on validation report)
    plan_levels = eligibility_data.get('planLevels', [])
    for plan_level in plan_levels:
        if plan_level.get('level') == 'deductibleInfo':
            # Collect individual deductible amounts
            individual_levels = plan_level.get('individual', [])
            if individual_levels:
                for individual in individual_levels:
                    remaining = individual.get('remainingAmount')
                    if remaining is not None:
                        try:
                            amount = float(remaining)
                            all_deductible_amounts.append(('individual', amount))
                        except (ValueError, TypeError):
                            pass
            
            # Collect family deductible amounts
            family_levels = plan_level.get('family', [])
            if family_levels:
                for family in family_levels:
                    remaining = family.get('remainingAmount')
                    if remaining is not None:
                        try:
                            amount = float(remaining)
                            all_deductible_amounts.append(('family', amount))
                        except (ValueError, TypeError):
                            pass
    
    # Navigate to the rawGraphQLResponse structure as fallback
    raw_response = eligibility_data.get('rawGraphQLResponse', {})
    if raw_response:
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try all eligibility records for deductible information
        for eligibility in eligibility_list:
            plan_levels = eligibility.get('eligibilityInfo', {}).get('planLevels', [])
            for plan_level in plan_levels:
                if plan_level.get('level') == 'deductibleInfo':
                    # Collect individual deductible amounts
                    individual_levels = plan_level.get('individual', [])
                    if individual_levels:
                        for individual in individual_levels:
                            remaining = individual.get('remainingAmount')
                            if remaining is not None:
                                try:
                                    amount = float(remaining)
                                    all_deductible_amounts.append(('individual', amount))
                                except (ValueError, TypeError):
                                    pass
                    
                    # Collect family deductible amounts
                    family_levels = plan_level.get('family', [])
                    if family_levels:
                        for family in family_levels:
                            remaining = family.get('remainingAmount')
                            if remaining is not None:
                                try:
                                    amount = float(remaining)
                                    all_deductible_amounts.append(('family', amount))
                                except (ValueError, TypeError):
                                    pass
    
    # Select the most relevant deductible amount
    if all_deductible_amounts:
        # Strategy: Prefer individual over family, and prefer non-zero amounts
        # First, try to find non-zero individual amounts
        non_zero_individual = [amt for type_, amt in all_deductible_amounts if type_ == 'individual' and amt > 0]
        if non_zero_individual:
            return str(max(non_zero_individual))  # Return highest non-zero individual amount
        
        # If no non-zero individual, try non-zero family amounts
        non_zero_family = [amt for type_, amt in all_deductible_amounts if type_ == 'family' and amt > 0]
        if non_zero_family:
            return str(max(non_zero_family))  # Return highest non-zero family amount
        
        # If all amounts are zero, return the first individual amount (or family if no individual)
        individual_amounts = [amt for type_, amt in all_deductible_amounts if type_ == 'individual']
        if individual_amounts:
            return str(individual_amounts[0])
        
        # Fallback to first family amount
        family_amounts = [amt for type_, amt in all_deductible_amounts if type_ == 'family']
        if family_amounts:
            return str(family_amounts[0])
    
    return "Not Found"

def extract_legacy_insurance_info(policy):
    """Extract insurance information from legacy API response format"""
    insurance_info = policy.get("insuranceInfo", {})
    return {
        'insuranceType': insurance_info.get("insuranceType", ""),
        'insuranceTypeCode': insurance_info.get("insuranceTypeCode", ""),
        'memberId': insurance_info.get("memberId", ""),
        'payerId': insurance_info.get("payerId", "")
    }

def extract_super_connector_insurance_info(eligibility_data):
    """Extract insurance information from Super Connector API response format"""
    if not eligibility_data:
        return {'insuranceType': '', 'insuranceTypeCode': '', 'memberId': '', 'payerId': ''}
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
            if insurance_info:
                return {
                    'insuranceType': insurance_info.get("planTypeDescription", ""),
                    'insuranceTypeCode': insurance_info.get("productServiceCode", ""),
                    'memberId': insurance_info.get("memberId", ""),
                    'payerId': insurance_info.get("payerId", "")
                }
        
        # Check for data in error extensions (some APIs return data here despite errors)
        errors = raw_response.get('errors', [])
        for error in errors:
            extensions = error.get('extensions', {})
            if extensions and 'details' in extensions:
                details = extensions.get('details', [])
                if details:
                    # Use the first detail record that has insurance info
                    for detail in details:
                        if detail.get('memberId') or detail.get('payerId'):
                            # Try to determine insurance type from available data
                            insurance_type = detail.get('planType', '')
                            if not insurance_type:
                                insurance_type = detail.get('productType', '')
                            
                            return {
                                'insuranceType': insurance_type,
                                'insuranceTypeCode': detail.get("productServiceCode", ""),
                                'memberId': detail.get("memberId", ""),
                                'payerId': detail.get("payerId", "")
                            }
    
    # Fallback to top-level fields
    insurance_type = eligibility_data.get("planTypeDescription", "")
    if not insurance_type:
        insurance_type = eligibility_data.get("productType", "")
    
    # Clean up the insurance type if it's too long (like the LPPO description)
    if insurance_type and len(insurance_type) > 50:
        # Extract just the plan type part
        if "PPO" in insurance_type:
            insurance_type = "Preferred Provider Organization (PPO)"
        elif "HMO" in insurance_type:
            insurance_type = "Health Maintenance Organization (HMO)"
        elif "EPO" in insurance_type:
            insurance_type = "Exclusive Provider Organization (EPO)"
        elif "POS" in insurance_type:
            insurance_type = "Point of Service (POS)"
    
    # Get insurance type code from multiple possible locations
    insurance_type_code = eligibility_data.get("productServiceCode", "")
    if not insurance_type_code:
        # Try to get from coverageTypes
        coverage_types = eligibility_data.get("coverageTypes", [])
        if coverage_types:
            insurance_type_code = coverage_types[0].get("typeCode", "")
    
    # Note: We're not mapping "M" to "PR" as "M" likely means "Medical" 
    # and "PR" should be "12" for PPO according to CMS standards
    # This mapping should be handled by the API developers
    
    return {
        'insuranceType': insurance_type,
        'insuranceTypeCode': insurance_type_code,
        'memberId': eligibility_data.get("subscriberId", ""),
        'payerId': eligibility_data.get("payerId", "")  # Use payerId instead of legalEntityCode (this should be payer_id from the inputs)
    }

def extract_legacy_policy_status(policy):
    """Extract policy status from legacy API response format"""
    policy_info = policy.get("policyInfo", {})
    return policy_info.get("policyStatus", "")

def extract_super_connector_policy_status(eligibility_data):
    """Extract policy status from Super Connector API response format"""
    if not eligibility_data:
        return ""
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
            if insurance_info:
                return insurance_info.get("policyStatus", "")
    
    # Fallback to top-level field
    return eligibility_data.get("policyStatus", "")

def is_legacy_response_format(data):
    """Determine if the response is in legacy format (has memberPolicies)"""
    return data is not None and "memberPolicies" in data

def is_super_connector_response_format(data):
    """Determine if the response is in Super Connector format (has rawGraphQLResponse)"""
    return data is not None and "rawGraphQLResponse" in data

# Function to extract required fields and display in a tabular format
def display_eligibility_info(data, dob, member_id, output_file):
    if data is None:
        return

    # Determine which API response format we're dealing with
    if is_legacy_response_format(data):
        # Handle legacy API response format
        for policy in data.get("memberPolicies", []):
            # Skip non-medical policies
            if policy.get("policyInfo", {}).get("coverageType", "") != "Medical":
                continue

            patient_info = extract_legacy_patient_info(policy)
            remaining_amount = extract_legacy_remaining_amount(policy)
            insurance_info = extract_legacy_insurance_info(policy)
            policy_status = extract_legacy_policy_status(policy)

            patient_name = "{} {} {}".format(
                patient_info['firstName'], 
                patient_info['middleName'], 
                patient_info['lastName']
            ).strip()[:20]

            # Display patient information in a table row format
            table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                patient_name, dob, insurance_info['insuranceType'], 
                insurance_info['payerId'], policy_status, remaining_amount)
            output_file.write(table_row + "\n")
            print(table_row)  # Print to console for progressive display

    elif is_super_connector_response_format(data):
        # Handle Super Connector API response format
        patient_info = extract_super_connector_patient_info(data)
        remaining_amount = extract_super_connector_remaining_amount(data)
        insurance_info = extract_super_connector_insurance_info(data)
        policy_status = extract_super_connector_policy_status(data)

        patient_name = "{} {} {}".format(
            patient_info['firstName'], 
            patient_info['middleName'], 
            patient_info['lastName']
        ).strip()[:20]

        # Display patient information in a table row format
        table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
            patient_name, dob, insurance_info['insuranceType'], 
            insurance_info['payerId'], policy_status, remaining_amount)
        output_file.write(table_row + "\n")
        print(table_row)  # Print to console for progressive display

    else:
        # Unknown response format - log for debugging
        MediLink_ConfigLoader.log("Unknown response format in display_eligibility_info", level="WARNING")
        MediLink_ConfigLoader.log("Response structure: {}".format(json.dumps(data, indent=2)), level="DEBUG")

# Main Execution Flow
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MEDILINK DEDUCTIBLE LOOKUP TOOL")
    print("=" * 80)
    print("This tool provides manual and batch eligibility lookups with validation.")
    print("Validation reports compare legacy vs Super Connector API responses.")
    print("=" * 80)
    
    while True:
        print("\nChoose an option:")
        print("1. Manual Patient Lookup (with validation)")
        print("2. Batch CSV Processing (with validation)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Step 1: Handle Manual Deductible Lookups
            manual_deductible_lookup()
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to perform another operation? (Y/N): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("\nExiting. Thank you for using MediLink Deductible Tool!")
                break
                
        elif choice == "2":
            # Step 2: Proceed with Existing CSV Processing
            print("\n--- Starting Batch Eligibility Processing ---")
            print("Processing {} patients from CSV data...".format(len(patients)))
            
            # Ask for confirmation before starting batch processing
            confirm = input("Proceed with batch processing? (Y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Batch processing cancelled.")
                continue
            
            output_file_path = os.path.join(os.getenv('TEMP'), 'eligibility_report.txt')
            with open(output_file_path, 'w') as output_file:
                table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                    "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
                output_file.write(table_header + "\n")
                output_file.write("-" * len(table_header) + "\n")
                print(table_header)
                print("-" * len(table_header))

                # Set to keep track of processed patients
                processed_patients = set()

                # Loop through each payer_id and patient to call the API, then display the eligibility information
                errors = []
                validation_reports = []
                total_patients = len(patients) * len(payer_ids)
                processed_count = 0
                
                for payer_id in payer_ids:
                    for dob, member_id in patients:
                        # Skip if this patient has already been processed
                        if (dob, member_id) in processed_patients:
                            continue
                        try:
                            processed_count += 1
                            print("Processing patient {}/{}: Member ID {}, DOB {}".format(
                                processed_count, total_patients, member_id, dob))
                            
                            # Run with validation enabled for batch processing
                            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, dob, member_id, npi, run_validation=True)
                            if eligibility_data is not None:
                                display_eligibility_info(eligibility_data, dob, member_id, output_file)  # Display as we get the result
                                processed_patients.add((dob, member_id))  # Mark this patient as processed
                        except Exception as e:
                            errors.append((dob, member_id, str(e)))

                # Display errors if any
                if errors:
                    error_msg = "\nErrors encountered during API calls:\n"
                    output_file.write(error_msg)
                    print(error_msg)
                    for error in errors:
                        error_details = "DOB: {}, Member ID: {}, Error: {}\n".format(error[0], error[1], error[2])
                        output_file.write(error_details)
                        print(error_details)

            # Ask if user wants to open the report
            open_report = input("\nBatch processing complete! Open the eligibility report? (Y/N): ").strip().lower()
            if open_report in ['y', 'yes']:
                os.system('notepad.exe "{}"'.format(output_file_path))
            
            # Print summary of validation reports
            print("\n" + "=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            print("Validation reports have been generated for each patient processed.")
            print("Each report compares the legacy API response with the Super Connector API response.")
            print("Check the TEMP directory for validation_report_*.txt files.")
            print("=" * 80)
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to perform another operation? (Y/N): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("\nExiting. Thank you for using MediLink Deductible Tool!")
                break
                
        elif choice == "3":
            print("\nExiting. Thank you for using MediLink Deductible Tool!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")