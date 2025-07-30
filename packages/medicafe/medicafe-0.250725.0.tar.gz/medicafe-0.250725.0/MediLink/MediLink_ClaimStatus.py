# MediLink_ClaimStatus.py
from datetime import datetime, timedelta
import os
import time
import json
import MediLink_API_v3

try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

# Load configuration
config, _ = MediLink_ConfigLoader.load_configuration()

# Calculate start_date as 60 days before today's date and end_date as today's date
end_date = datetime.today()
start_date = end_date - timedelta(days=60)
end_date_str = end_date.strftime('%m/%d/%Y')
start_date_str = start_date.strftime('%m/%d/%Y')

# Get billing provider TIN from configuration
billing_provider_tin = config['MediLink_Config'].get('billing_provider_tin')

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '37602']
# Allowed payer id's for UHC 87726, 03432, 96385, 95467, 86050, 86047, 95378, 37602. This api does not support payerId 06111.

# Initialize the API client
client = MediLink_API_v3.APIClient()

class ClaimCache:
    """In-memory cache for API responses"""
    def __init__(self):
        self.cache = {}  # {cache_key: {'data': response, 'payer_id': payer_id}}
    
    def get_cache_key(self, tin, start_date, end_date, payer_id):
        """Generate unique cache key for API call parameters"""
        return "{}_{}_{}_{}".format(tin, start_date, end_date, payer_id)
    
    def is_cached(self, cache_key):
        """Check if response is cached"""
        return cache_key in self.cache
    
    def get_cached_response(self, cache_key):
        """Retrieve cached response"""
        return self.cache[cache_key]['data']
    
    def cache_response(self, cache_key, response, payer_id):
        """Cache API response"""
        self.cache[cache_key] = {
            'data': response,
            'payer_id': payer_id
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()

class ConsolidatedClaims:
    """Consolidated claims data structure"""
    def __init__(self):
        self.claims_by_number = {}  # {claim_number: {claim_data, payer_sources: [payer_ids]}}
        self.payer_ids_checked = set()
        self.duplicate_warnings = []
    
    def add_claim(self, claim_data, payer_id):
        """Add claim to consolidated data, tracking payer sources"""
        claim_number = claim_data['claim_number']
        
        if claim_number not in self.claims_by_number:
            self.claims_by_number[claim_number] = {
                'data': claim_data,
                'payer_sources': [payer_id]
            }
        else:
            # Check if this is a duplicate with different data
            existing_data = self.claims_by_number[claim_number]['data']
            if self._claims_equal(existing_data, claim_data):
                # Same data, just add payer source
                if payer_id not in self.claims_by_number[claim_number]['payer_sources']:
                    self.claims_by_number[claim_number]['payer_sources'].append(payer_id)
            else:
                # Different data - create warning
                self.duplicate_warnings.append({
                    'claim_number': claim_number,
                    'existing_payers': self.claims_by_number[claim_number]['payer_sources'],
                    'new_payer': payer_id,
                    'existing_data': existing_data,
                    'new_data': claim_data
                })
        
        self.payer_ids_checked.add(payer_id)
    
    def _claims_equal(self, claim1, claim2):
        """Compare two claim data structures for equality"""
        # Compare key fields that should be identical for the same claim
        key_fields = ['claim_status', 'patient_name', 'processed_date', 'first_service_date', 
                     'total_charged_amount', 'total_allowed_amount', 'total_paid_amount', 
                     'total_patient_responsibility_amount']
        
        for field in key_fields:
            if claim1.get(field) != claim2.get(field):
                return False
        return True

def extract_claim_data(claim):
    """Extract standardized claim data from API response"""
    claim_number = claim['claimNumber']
    claim_status = claim['claimStatus']
    patient_first_name = claim['memberInfo']['ptntFn']
    patient_last_name = claim['memberInfo']['ptntLn']
    processed_date = claim['claimSummary']['processedDt']
    first_service_date = claim['claimSummary']['firstSrvcDt']
    total_charged_amount = claim['claimSummary']['totalChargedAmt']
    total_allowed_amount = claim['claimSummary']['totalAllowdAmt']
    total_paid_amount = claim['claimSummary']['totalPaidAmt']
    total_patient_responsibility_amount = claim['claimSummary']['totalPtntRespAmt']
    
    patient_name = "{} {}".format(patient_first_name, patient_last_name)
    
    return {
        'claim_number': claim_number,
        'claim_status': claim_status,
        'patient_name': patient_name,
        'processed_date': processed_date,
        'first_service_date': first_service_date,
        'total_charged_amount': total_charged_amount,
        'total_allowed_amount': total_allowed_amount,
        'total_paid_amount': total_paid_amount,
        'total_patient_responsibility_amount': total_patient_responsibility_amount,
        'claim_xwalk_data': claim['claimSummary']['clmXWalkData']
    }

def process_claims_with_payer_rotation(billing_provider_tin, start_date_str, end_date_str, 
                                     payer_ids, cache, consolidated_claims):
    """
    Process claims across multiple payer IDs with caching and consolidation
    """
    client = MediLink_API_v3.APIClient()
    
    for payer_id in payer_ids:
        print("Processing Payer ID: {}".format(payer_id))
        
        # Generate cache key
        cache_key = cache.get_cache_key(billing_provider_tin, start_date_str, end_date_str, payer_id)
        
        # Check cache first
        if cache.is_cached(cache_key):
            print("  Using cached response for Payer ID: {}".format(payer_id))
            claim_summary = cache.get_cached_response(cache_key)
        else:
            print("  Making API call for Payer ID: {}".format(payer_id))
            try:
                claim_summary = MediLink_API_v3.get_claim_summary_by_provider(
                    client, billing_provider_tin, start_date_str, end_date_str, payer_id=payer_id
                )
                cache.cache_response(cache_key, claim_summary, payer_id)
            except Exception as e:
                print("  Error processing Payer ID {}: {}".format(payer_id, e))
                continue
        
        # Process claims from this payer
        claims = claim_summary.get('claims', [])
        for claim in claims:
            claim_data = extract_claim_data(claim)
            consolidated_claims.add_claim(claim_data, payer_id)

def display_consolidated_claims(consolidated_claims, output_file):
    """
    Display consolidated claims with payer ID header and duplicate warnings
    """
    # Display header with all payer IDs checked
    payer_ids_str = ", ".join(sorted(consolidated_claims.payer_ids_checked))
    header = "Payer IDs Checked: {} | Start Date: {} | End Date: {}".format(
        payer_ids_str, start_date_str, end_date_str)
    print(header)
    output_file.write(header + "\n")
    print("=" * len(header))
    output_file.write("=" * len(header) + "\n")
    
    # Table header
    table_header = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7} | {:<15}".format(
        "Claim #", "Status", "Patient", "Proc.", "Serv.", "Allowed", "Paid", "Pt Resp", "Charged", "Payer Sources")
    print(table_header)
    output_file.write(table_header + "\n")
    print("-" * len(table_header))
    output_file.write("-" * len(table_header) + "\n")
    
    # Sort claims by first service date
    sorted_claims = sorted(
        consolidated_claims.claims_by_number.items(),
        key=lambda x: x[1]['data']['first_service_date']
    )
    
    # Display each claim
    for claim_number, claim_info in sorted_claims:
        claim_data = claim_info['data']
        payer_sources = claim_info['payer_sources']
        
        # Format payer sources
        payer_sources_str = ", ".join(sorted(payer_sources))
        
        table_row = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7} | {:<15}".format(
            claim_number, claim_data['claim_status'], claim_data['patient_name'][:20],
            claim_data['processed_date'][:5], claim_data['first_service_date'][:5],
            claim_data['total_allowed_amount'], claim_data['total_paid_amount'],
            claim_data['total_patient_responsibility_amount'], claim_data['total_charged_amount'],
            payer_sources_str
        )
        print(table_row)
        output_file.write(table_row + "\n")
        
        # Display crosswalk data for $0.00 claims
        if claim_data['total_paid_amount'] == '0.00':
            for xwalk in claim_data['claim_xwalk_data']:
                clm507Cd = xwalk['clm507Cd']
                clm507CdDesc = xwalk['clm507CdDesc']
                clm508Cd = xwalk['clm508Cd']
                clm508CdDesc = xwalk['clm508CdDesc']
                clmIcnSufxCd = xwalk['clmIcnSufxCd']
                print("  507: {} ({}) | 508: {} ({}) | ICN Suffix: {}".format(
                    clm507Cd, clm507CdDesc, clm508Cd, clm508CdDesc, clmIcnSufxCd))
    
    # Display duplicate warnings (terminal and log only, not file)
    if consolidated_claims.duplicate_warnings:
        print("\n" + "="*80)
        print("DUPLICATE CLAIM WARNINGS:")
        print("="*80)
        
        for warning in consolidated_claims.duplicate_warnings:
            warning_msg = (
                "Claim {} found in multiple payers with different data:\n"
                "  Existing payers: {}\n"
                "  New payer: {}\n"
                "  Status difference: {} vs {}\n"
                "  Amount difference: ${} vs ${}".format(
                    warning['claim_number'],
                    ", ".join(warning['existing_payers']),
                    warning['new_payer'],
                    warning['existing_data']['claim_status'],
                    warning['new_data']['claim_status'],
                    warning['existing_data']['total_paid_amount'],
                    warning['new_data']['total_paid_amount']
                )
            )
            print(warning_msg)
            
            # Log the warning
            MediLink_ConfigLoader.log(
                "Duplicate claim warning: {}".format(warning_msg),
                level="WARNING"
            )

# Initialize cache and consolidated claims
cache = ClaimCache()
consolidated_claims = ConsolidatedClaims()

# Process claims with payer rotation
process_claims_with_payer_rotation(
    billing_provider_tin, start_date_str, end_date_str, payer_ids, cache, consolidated_claims
)

# Display consolidated results
output_file_path = os.path.join(os.getenv('TEMP'), 'claim_summary_report.txt')
with open(output_file_path, 'w') as output_file:
    display_consolidated_claims(consolidated_claims, output_file)

# Clear cache after consolidated table is generated
cache.clear_cache()

# Open the generated file in Notepad
os.startfile(output_file_path)  # Use os.startfile for better handling