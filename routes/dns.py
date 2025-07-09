# routes/dns.py

from flask import Blueprint, request, jsonify
import dns.resolver
import dns.exception
import re
from config import Config
from utils import get_record_type_name, create_response

dns_bp = Blueprint('dns', __name__)

@dns_bp.route('/dns_lookup', methods=['GET'])
def dns_lookup():
    """
    Performs various DNS record lookups for a given domain.
    """
    domain = request.args.get('domain')

    if not domain:
        response, status_code = create_response(
            success=False,
            message='Please provide a domain name.',
            status_code=400
        )
        return jsonify(response), status_code

    # Basic validation for domain format
    if not re.match(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", domain, re.IGNORECASE):
        response, status_code = create_response(
            success=False,
            message='Invalid domain format. Please enter a valid domain (e.g., example.com).',
            status_code=400
        )
        return jsonify(response), status_code

    all_records = {}
    found_any_record = False
    errors = []

    try:
        # Define the DNS record types you want to fetch
        record_types = [
            'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR', 'CAA'
        ]

        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        for rtype_str in record_types:
            try:
                answers = resolver.resolve(domain, rtype_str)
                formatted_records = []
                for rdata in answers:
                    formatted_entry = {}
                    # Common fields
                    formatted_entry['host'] = answers.qname.to_text(omit_final_dot=True)
                    formatted_entry['type'] = rtype_str
                    formatted_entry['ttl'] = answers.ttl

                    # Specific fields based on record type
                    if rtype_str in ['A', 'AAAA']:
                        formatted_entry['ip'] = str(rdata)
                    elif rtype_str == 'MX':
                        formatted_entry['pri'] = rdata.preference
                        formatted_entry['target'] = rdata.exchange.to_text(omit_final_dot=True)
                    elif rtype_str == 'NS':
                        formatted_entry['target'] = rdata.target.to_text(omit_final_dot=True)
                    elif rtype_str == 'TXT':
                        formatted_entry['txt'] = "".join([s.decode('utf-8') for s in rdata.strings])
                    elif rtype_str == 'CNAME':
                        formatted_entry['target'] = rdata.target.to_text(omit_final_dot=True)
                    elif rtype_str == 'SOA':
                        formatted_entry['mname'] = rdata.mname.to_text(omit_final_dot=True)
                        formatted_entry['rname'] = rdata.rname.to_text(omit_final_dot=True)
                        formatted_entry['serial'] = rdata.serial
                        formatted_entry['refresh'] = rdata.refresh
                        formatted_entry['retry'] = rdata.retry
                        formatted_entry['expire'] = rdata.expire
                        formatted_entry['minimum-ttl'] = rdata.minimum
                    elif rtype_str == 'SRV':
                        formatted_entry['priority'] = rdata.priority
                        formatted_entry['weight'] = rdata.weight
                        formatted_entry['port'] = rdata.port
                        formatted_entry['target'] = rdata.target.to_text(omit_final_dot=True)
                    elif rtype_str == 'PTR':
                        formatted_entry['target'] = rdata.target.to_text(omit_final_dot=True)
                    elif rtype_str == 'CAA':
                        formatted_entry['flags'] = rdata.flags
                        formatted_entry['tag'] = rdata.tag.decode('utf-8')
                        formatted_entry['value'] = rdata.value.decode('utf-8')

                    formatted_records.append(formatted_entry)

                if formatted_records:
                    found_any_record = True
                    all_records[rtype_str] = formatted_records

            except dns.resolver.NoAnswer:
                pass # No records of this type found
            except dns.resolver.NXDOMAIN:
                # This means the domain itself does not exist.
                # We can break early or let it collect other errors.
                # For now, we'll let it try other types and report overall.
                pass
            except dns.exception.Timeout:
                errors.append(f"DNS query for {rtype_str} timed out.")
            except Exception as e:
                errors.append(f"Error querying {rtype_str} records: {e}")

        if not found_any_record:
            if not errors: # If no records and no specific errors, it's likely NXDOMAIN or truly no records
                errors.append('No DNS records found for this domain or domain does not exist. Please check the spelling.')
            response, status_code = create_response(
                success=False,
                message='No DNS records found or domain does not exist.',
                data={'domain': domain, 'records': {}},
                errors=errors,
                status_code=404 # Use 404 if domain doesn't exist or no records
            )
        else:
            response, status_code = create_response(
                success=True,
                message='DNS records fetched successfully.',
                data={'domain': domain, 'records': all_records},
                errors=errors,
                status_code=200
            )

    except Exception as e:
        errors.append(f'An unexpected error occurred: {e}')
        response, status_code = create_response(
            success=False,
            message=f'An unexpected error occurred: {e}',
            errors=errors,
            status_code=500
        )

    return jsonify(response), status_code