from typing import List, Dict


class ApprovalCalculationService:
    def calculate_variant_summary(self, all_related_grs: List, current_gr):
        variant_summary = {}

        for related_gr in all_related_grs:
            is_current = related_gr.id == current_gr.id
            is_approved = related_gr.status in ['approved', 'completed', 'has_issue']

            if not is_current and not is_approved:
                continue

            for detail in related_gr.receipt_details:
                variant_id = str(detail.product_variant_id)
                po_detail_id = str(detail.po_detail_id)

                if variant_id not in variant_summary:
                    variant_summary[variant_id] = {
                        'po_detail_id': po_detail_id,
                        'total_accepted': 0
                    }

                variant_summary[variant_id]['total_accepted'] += detail.accepted_quantity

        return variant_summary

    def determine_completion_status(self, variant_summary: Dict[str, Dict], po_details_map: Dict[str, any]):
        all_completed = True
        comparison_details = []

        processed_po_detail_ids = set()

        for variant_id, summary in variant_summary.items():
            po_detail_id = summary['po_detail_id']
            po_detail = po_details_map.get(po_detail_id)

            if not po_detail:
                continue

            processed_po_detail_ids.add(po_detail_id)

            ordered_qty = po_detail.quantity
            total_accepted_qty = summary['total_accepted']
            is_complete = total_accepted_qty >= ordered_qty

            comparison_details.append({
                'variant_id': variant_id,
                'po_detail_id': po_detail_id,
                'ordered': ordered_qty,
                'total_accepted': total_accepted_qty,
                'remaining': max(0, ordered_qty - total_accepted_qty),
                'is_complete': is_complete
            })

            if not is_complete:
                all_completed = False

        for po_detail_id, po_detail in po_details_map.items():
            if po_detail_id not in processed_po_detail_ids:
                all_completed = False
                comparison_details.append({
                    'variant_id': str(po_detail.product_variant_id),
                    'po_detail_id': po_detail_id,
                    'ordered': po_detail.quantity,
                    'total_accepted': 0,
                    'remaining': po_detail.quantity,
                    'is_complete': False
                })

        gr_status = "completed" if all_completed else "has_issue"

        return {
            'gr_status': gr_status,
            'all_completed': all_completed,
            'comparison_details': comparison_details
        }