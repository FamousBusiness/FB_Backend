import pdfkit
from django.core.files.base import ContentFile
from PremiumPlan.models import PremiumPlanOrder
from Listings.models import Business
from uuid import uuid4




def generate_pdf(request_user, premium_plan_order):
    business = Business.objects.get(owner = request_user)

    plan_amount = int(premium_plan_order.amount)
    gst         = (plan_amount / 100) * 18
    
    
    premium_plan = premium_plan_order.premium_plan
    lead_view_quantity = premium_plan.lead_view if premium_plan else 0

    random_invoice_no = str(uuid4())[:25]

    html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                        }}
                        .header {{
                            text-align: center;
                            font-size: 24px;
                            font-weight: bold;
                        }}
                        .sub-header {{
                            text-align: center;
                            font-size: 18px;
                        }}
                        .from-to {{
                            display: flex;
                            justify-content: space-between;
                            margin: 20px 0;
                        }}
                        .from, .to {{
                            width: 45%;
                        }}
                        .from h3, .to h3 {{
                            margin-bottom: 5px;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        th, td {{
                            border: 1px solid #000;
                            padding: 10px;
                            text-align: left;
                        }}
                        .total {{
                            text-align: right;
                            margin-top: 20px;
                        }}
                        .note {{
                            margin-top: 30px;
                            font-size: 12px;
                        }}
                    </style>
                </head>

                <body>
                    <div class="header">TAX INVOICE</div>

                    <div class="sub-header">Famous Business</div>

                    <div class="from-to">
                        <div class="from">
                            <h3>FROM:</h3>
                            <p>WEBZOTICA BUSINESS FAMOUS SOFTWARE PRIVATE LIMITED<br>
                            Faridabad, Haryana, India<br>
                            GSTIN: 06AADCW6644C1ZF</p>
                        </div>

                        <div class="to">
                            <h3>Billing To:</h3>
                            <p>{business.business_name}<br/>
                                {business.city}, {business.state}, India<br>
                            </p>
                        </div>
                    </div>

                    <div>Date: 28/12/2024<br>INVOICE No: {random_invoice_no}</div>

                    <table>
                        <tr>
                            <th>Item Description</th>
                            <th>Qty</th>
                            <th>HSN Code</th>
                            <th>Unit Price</th>
                            <th>Total Price</th>
                        </tr>
                        <tr>
                            <td>Business Plan Subscription</td>
                            <td>{premium_plan_order.premium_plan}</td>
                            <td>998361</td>
                            <td>Rs.{plan_amount - gst}</td>
                            <td>Rs.{plan_amount - gst}</td>
                        </tr>
                    </table>

                    <p>(The Business Plan offers {lead_view_quantity} leads/month)</p>

                    <div class="total">
                        SUB TOTAL: Rs.{plan_amount - gst}<br>
                        TAX (18%): Rs.{gst}<br>
                        GRAND TOTAL: Rs.{plan_amount}
                    </div>

                    <div class="note">
                        <p>Note: This invoice is auto-generated and does not require a signature. For any queries, please contact<br>
                        customercare@famousbusiness.in  Helpline: 080-62181258</p>
                    </div>
                </body>
            </html>
        """
    
    pdf_bytes = pdfkit.from_string(html_content, False)

    premium_plan_order.invoice.save(
            f'invoice{premium_plan_order.pk}.pdf',
            ContentFile(pdf_bytes)
        )
    
    premium_plan_order.invoice_no = random_invoice_no
    premium_plan_order.save()

