import streamlit as st
import sys
import os
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, save_data, generate_id, get_current_datetime, add_record
import pandas as pd

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# All users can add advance payment data, admin can edit/delete
user_role = st.session_state.get('user_role', 'User')

st.title("💳 Advance Payments Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
advance_payments = load_data('advance_payments.json', selected_hotel)
rooms = load_data('rooms.json', selected_hotel)

# Advance payments overview
st.markdown("### Advance Payments Overview")

# Calculate totals
total_advances = len(advance_payments)
total_amount = sum(ap.get('actual_amount', ap.get('amount', 0)) for ap in advance_payments)
pending_advances = len([ap for ap in advance_payments if ap['status'] in ['Pending', 'Partially Received']])
fully_received = len([ap for ap in advance_payments if ap['status'] == 'Completed'])
refunded_advances = len([ap for ap in advance_payments if ap['status'] == 'Refunded'])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Advances", total_advances)
with col2:
    st.metric("Total Amount", f"₹{total_amount:,.2f}")
with col3:
    st.metric("Pending", pending_advances)
with col4:
    st.metric("Completed", fully_received)

st.markdown("---")

# Add new advance payment
st.markdown("### Record Advance Payment")

with st.form("add_advance_payment_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        customer_contact = st.text_input("Contact Number", placeholder="Phone number")
        customer_email = st.text_input("Email Address", placeholder="Email (optional)")
        
        # Room selection (optional for advance bookings) - load from current hotel
        selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
        rooms = load_data('rooms.json', selected_hotel)
        if isinstance(rooms, dict):
            all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))]
        elif isinstance(rooms, list):
            all_rooms = [f"Room {room.get('room_number', room.get('id', i+101))}" for i, room in enumerate(rooms)]
        else:
            all_rooms = [f"Room {i}" for i in range(101, 109)]
        room_options = ["Not Selected"] + all_rooms
        selected_room = st.selectbox("Room Number (if known)", room_options)
        
        booking_date = st.date_input("Expected Booking Date", value=None, help="Expected check-in date")
    
    with col2:
        advance_amount = st.number_input("Advance Amount", min_value=0.0, step=100.0, format="%.2f")
        remaining_amount = st.number_input("Remaining Amount", min_value=0.0, step=100.0, format="%.2f", help="Remaining amount to be paid later")
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Bank Transfer", "Cheque"])
        
        if payment_method == "Cheque":
            cheque_number = st.text_input("Cheque Number", placeholder="Enter cheque number")
            cheque_date = st.date_input("Cheque Date")
        else:
            cheque_number = ""
            cheque_date = None
        
        if payment_method in ["Card", "UPI"]:
            transaction_id = st.text_input("Transaction ID", placeholder="Enter transaction ID")
        else:
            transaction_id = ""
        
        purpose = st.selectbox("Purpose", [
            "Room Booking",
            "Event Booking",
            "Conference Room",
            "Wedding/Function",
            "Corporate Booking",
            "Other"
        ])
        
        notes = st.text_area("Notes", placeholder="Additional notes about the advance payment")
    
    submit_advance = st.form_submit_button("Record Advance Payment", type="primary")
    
    if submit_advance:
        if not customer_name or advance_amount <= 0:
            st.error("Customer name and valid advance amount are required")
        elif payment_method == "Cheque" and not cheque_number:
            st.error("Cheque number is required for cheque payments")
        else:
            total_amount = advance_amount + remaining_amount
            new_advance = {
                'id': generate_id(),
                'date': booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking_date else get_current_datetime(),
                'customer_name': customer_name,
                'customer_contact': customer_contact,
                'customer_email': customer_email,
                'room_number': selected_room if selected_room != "Not Selected" else None,
                'booking_date': str(booking_date) if booking_date else None,
                'advance_amount': advance_amount,
                'remaining_amount': remaining_amount,
                'total_amount': total_amount,
                'amount': total_amount,  # Use total amount as main amount
                'payment_method': payment_method,
                'cheque_number': cheque_number,
                'cheque_date': str(cheque_date) if cheque_date else None,
                'transaction_id': transaction_id,
                'purpose': purpose,
                'notes': notes,
                'status': 'Pending' if remaining_amount > 0 else 'Fully Received',
                'received_amount': 0,
                'created_by': st.session_state.get('username', 'Unknown')
            }
            
            advance_payments.append(new_advance)
            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
            save_data('advance_payments.json', advance_payments, selected_hotel)
            
            # Immediately add the advance payment to sales on the advance date
            sales = load_data('sales.json', selected_hotel)
            # Determine payment type for sales (Cash/Account)
            sales_payment_type = "Cash" if payment_method in ["Cash", "UPI"] else "Account"
            
            new_sale = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'transaction_date': get_current_datetime(),
                'type': 'Advance Payment - Initial',
                'amount': advance_amount,  # Only the advance amount, not total
                'payment_type': sales_payment_type,
                'customer_name': customer_name,
                'description': f"Initial advance payment #{new_advance['id']} - ₹{advance_amount:,.2f} (Total booking: ₹{total_amount:,.2f}, Remaining: ₹{remaining_amount:,.2f})",
                'advance_id': new_advance['id'],
                'status': 'Completed',
                'created_by': st.session_state.get('username', 'Unknown')
            }
            sales.append(new_sale)
            save_data('sales.json', sales, selected_hotel)
            
            st.success(f"Advance payment recorded successfully! ₹{advance_amount:,.2f} added to {sales_payment_type.lower()} sales.")
            st.rerun()

st.markdown("---")

# Advance payments list
st.markdown("### Advance Payments Records")

if advance_payments:
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Partially Received", "Completed", "Refunded", "Expired"])
    with col2:
        filter_payment_method = st.selectbox("Filter by Payment Method", ["All"] + list(set(ap['payment_method'] for ap in advance_payments)))
    with col3:
        filter_purpose = st.selectbox("Filter by Purpose", ["All"] + list(set(ap['purpose'] for ap in advance_payments)))
    
    # Apply filters
    filtered_advances = advance_payments
    if filter_status != "All":
        filtered_advances = [ap for ap in filtered_advances if ap['status'] == filter_status]
    if filter_payment_method != "All":
        filtered_advances = [ap for ap in filtered_advances if ap['payment_method'] == filter_payment_method]
    if filter_purpose != "All":
        filtered_advances = [ap for ap in filtered_advances if ap['purpose'] == filter_purpose]
    
    # Display advance payments
    for advance in filtered_advances:
        # Color coding based on status
        if advance['status'] == 'Pending':
            border_color = "#ffa500"
        elif advance['status'] == 'Utilized':
            border_color = "#28a745"
        elif advance['status'] == 'Refunded':
            border_color = "#dc3545"
        else:
            border_color = "#6c757d"
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; padding-left: 10px; margin-bottom: 10px;">
            """, unsafe_allow_html=True)
            
            # Show completion date if completed, otherwise advance date
            if advance['status'] == 'Completed' and advance.get('completion_date'):
                display_date = advance['completion_date'][:10] if advance['completion_date'] else advance['date'][:10] if advance['date'] else 'N/A'
                date_label = f"{display_date} (Completed)"
            else:
                display_date = advance['date'][:10] if advance['date'] else 'N/A'
                date_label = display_date
            
            total_amount = advance.get('total_amount', advance.get('amount', 0))
            with st.expander(f"#{advance['id']} - {advance['customer_name']} - ₹{total_amount:,.2f} - {date_label}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Advance Date:** {advance['date'][:10] if advance['date'] else 'N/A'}")
                    if advance['status'] == 'Completed' and advance.get('completion_date'):
                        st.write(f"**Completion Date:** {advance['completion_date'][:10]}")
                    st.write(f"**Customer:** {advance['customer_name']}")
                    st.write(f"**Contact:** {advance['customer_contact']}")
                    st.write(f"**Email:** {advance.get('customer_email', 'N/A')}")
                    
                    # Handle advance amount structure
                    advance_amt = advance.get('advance_amount', 0)
                    remaining_amt = advance.get('remaining_amount', 0)
                    total_amt = advance.get('total_amount', advance.get('amount', 0))
                    received_amt = advance.get('received_amount', 0)
                    
                    st.write(f"**Advance Amount:** ₹{advance_amt:,.2f}")
                    st.write(f"**Remaining Amount:** ₹{remaining_amt:,.2f}")
                    st.write(f"**Total Amount:** ₹{total_amt:,.2f}")
                    if received_amt > 0:
                        st.write(f"**Additional Received:** ₹{received_amt:,.2f}")
                    st.write(f"**Payment Method:** {advance['payment_method']}")
                
                with col2:
                    st.write(f"**Room:** {advance.get('room_number', 'Not Selected')}")
                    st.write(f"**Booking Date:** {advance.get('booking_date', 'Not Set')}")
                    st.write(f"**Purpose:** {advance['purpose']}")
                    # Status with color coding
                    status_color = "🟢" if advance['status'] == 'Completed' else "🟡" if advance['status'] == 'Partially Received' else "🔴"
                    st.write(f"**Status:** {status_color} {advance['status']}")
                    
                    # Show completion details for completed advances
                    if advance['status'] == 'Completed':
                        if advance.get('final_payment_method'):
                            st.write(f"**Final Payment Method:** {advance['final_payment_method']}")
                        if advance.get('completion_date'):
                            st.write(f"**Completed On:** {advance['completion_date'][:10]}")
                        st.write("✅ **Fully Settled - No Further Action Required**")
                    else:
                        # Show payment progress for pending advances
                        received_amount = advance.get('received_amount', 0)
                        if received_amount > 0:
                            st.write(f"**Additional Received:** ₹{received_amount:,.2f}")
                            remaining_to_pay = remaining_amt - received_amount
                            st.write(f"**Still Remaining:** ₹{remaining_to_pay:,.2f}")
                    
                    st.write(f"**Created By:** {advance.get('created_by', 'Unknown')}")
                
                # Payment details
                if advance.get('cheque_number'):
                    st.write(f"**Cheque Number:** {advance['cheque_number']}")
                    st.write(f"**Cheque Date:** {advance.get('cheque_date', 'N/A')}")
                
                if advance.get('transaction_id'):
                    st.write(f"**Transaction ID:** {advance['transaction_id']}")
                
                if advance.get('notes'):
                    st.write(f"**Notes:** {advance['notes']}")
                
                # Payment Collection - Only show for non-completed advances
                if advance['status'] in ['Pending', 'Partially Received'] and not advance.get('is_editable', True) == False:
                    # Handle new structure with custom remaining amounts
                    remaining_amt = advance.get('remaining_amount', 0)
                    received_amount = advance.get('received_amount', 0)
                    still_remaining = remaining_amt - received_amount
                    
                    if still_remaining > 0:
                        st.markdown("**💰 Collect Remaining Payment**")
                        with st.form(f"receive_payment_{advance['id']}"):
                            col_pay1, col_pay2 = st.columns(2)
                            with col_pay1:
                                st.write(f"**Remaining to Collect:** ₹{still_remaining:,.2f}")
                                st.write(f"**Already Collected:** ₹{received_amount:,.2f}")
                                payment_amount = st.number_input("Payment Amount", min_value=0.0, max_value=float(still_remaining), step=100.0, key=f"pay_amt_{advance['id']}")
                                payment_type = st.selectbox("Payment Type", ["Cash", "Account", "Discount", "Complementary"], key=f"pay_type_{advance['id']}")
                            with col_pay2:
                                payment_date = st.date_input("Payment Received Date", value=datetime.now().date(), help="Select the date when payment was received", key=f"pay_date_{advance['id']}")
                                st.write("")  # spacing
                                receive_btn = st.form_submit_button("💳 Receive Payment", type="primary")
                            
                            if receive_btn:
                                if payment_amount > 0:
                                    new_received = received_amount + payment_amount
                                    
                                    # Update advance payment - use selected payment date
                                    completion_datetime = f"{payment_date} {datetime.now().strftime('%H:%M:%S')}"
                                    for ap in advance_payments:
                                        if ap['id'] == advance['id']:
                                            ap['received_amount'] = new_received
                                            if new_received >= remaining_amt:
                                                ap['status'] = 'Completed'
                                                ap['completion_date'] = completion_datetime
                                                ap['final_payment_method'] = payment_type
                                                ap['is_editable'] = False  # Make non-editable after completion
                                            else:
                                                ap['status'] = 'Partially Received'
                                            break
                                    selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                    save_data('advance_payments.json', advance_payments, selected_hotel)
                                    
                                    # Add to respective section based on payment type
                                    if payment_type in ["Cash", "Account"]:
                                        # Add this payment amount to sales on the actual payment date
                                        sales = load_data('sales.json', selected_hotel)
                                        new_sale = {
                                            'id': generate_id(),
                                            'date': completion_datetime,  # Use actual payment date
                                            'transaction_date': completion_datetime,  # Actual payment date
                                            'type': 'Advance Payment - Remaining',
                                            'amount': payment_amount,  # Only the amount paid today
                                            'payment_type': payment_type,
                                            'customer_name': advance['customer_name'],
                                            'description': f"Remaining payment for advance #{advance['id']} - ₹{payment_amount:,.2f} (Originally advanced: {advance['date'][:10]}, Payment date: {str(payment_date)})",
                                            'original_advance_date': advance['date'][:10],
                                            'payment_date': str(payment_date),
                                            'advance_id': advance['id'],
                                            'status': 'Completed',
                                            'created_by': st.session_state.get('username', 'Unknown')
                                        }
                                        sales.append(new_sale)
                                        save_data('sales.json', sales, selected_hotel)
                                        success_msg = f"₹{payment_amount:,.2f} added to {payment_type.lower()} sales on {str(payment_date)}"
                                    
                                    elif payment_type == "Discount":
                                        # Add to discounts
                                        discounts = load_data('discounts.json', selected_hotel)
                                        new_discount = {
                                            'id': generate_id(),
                                            'date': completion_datetime,
                                            'customer_name': advance['customer_name'],
                                            'amount': payment_amount,
                                            'original_amount': payment_amount,
                                            'discount_type': 'Advance Payment Discount',
                                            'reason': f"Discount applied to advance payment #{advance['id']} - partial amount waived",
                                            'reference_id': advance['id'],
                                            'percentage': 0,
                                            'original_advance_date': advance['date'][:10],
                                            'advance_id': advance['id'],
                                            'created_by': st.session_state.get('username', 'Unknown')
                                        }
                                        discounts.append(new_discount)
                                        save_data('discounts.json', discounts, selected_hotel)
                                        success_msg = f"₹{payment_amount:,.2f} added to discount records on {str(payment_date)}"
                                    
                                    elif payment_type == "Complementary":
                                        # Add to complementary records
                                        complementary_records = load_data('complementary_records.json', selected_hotel)
                                        new_comp = {
                                            'id': generate_id(),
                                            'date': completion_datetime,
                                            'customer_name': advance['customer_name'],
                                            'amount': payment_amount,
                                            'type': 'Advance Payment Complementary',
                                            'reason': f"Complementary waiver for advance payment #{advance['id']} - partial amount waived",
                                            'reference_id': advance['id'],
                                            'original_advance_date': advance['date'][:10],
                                            'advance_id': advance['id'],
                                            'created_by': st.session_state.get('username', 'Unknown')
                                        }
                                        complementary_records.append(new_comp)
                                        save_data('complementary_records.json', complementary_records, selected_hotel)
                                        success_msg = f"₹{payment_amount:,.2f} added to complementary records on {str(payment_date)}"
                                    
                                    if new_received >= remaining_amt:
                                        st.success(f"Final payment completed! {success_msg}")
                                    else:
                                        st.success(f"{success_msg}. Remaining: ₹{remaining_amt - new_received:,.2f}")
                                    st.rerun()
                
                # Management actions row - Only show for non-completed advances
                if advance['status'] != 'Completed' and advance.get('is_editable', True) != False:
                    st.markdown("**⚙️ Management Actions**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        # Quick actions for pending advances
                        if advance['status'] in ['Pending', 'Partially Received']:
                            if st.button(f"✅ Mark Fully Paid", key=f"mark_paid_{advance['id']}", help="Mark as fully received - choose payment type"):
                                # Show payment type selection for marking as paid
                                with st.form(f"mark_paid_form_{advance['id']}"):
                                    st.write("**Select how the remaining amount was received:**")
                                    remaining_amt = advance.get('remaining_amount', 0)
                                    received_amount = advance.get('received_amount', 0)
                                    still_remaining = remaining_amt - received_amount
                                    
                                    st.write(f"Amount to be marked as received: ₹{still_remaining:,.2f}")
                                    
                                    payment_method = st.selectbox("Payment Method", 
                                                                ["Cash", "Account", "Discount", "Complementary"], 
                                                                key=f"mark_method_{advance['id']}")
                                    completion_date = st.date_input("Date Received", 
                                                                  value=datetime.now().date(), 
                                                                  key=f"mark_date_{advance['id']}")
                                    
                                    if st.form_submit_button("Confirm Mark as Paid"):
                                        completion_datetime = f"{completion_date} {datetime.now().strftime('%H:%M:%S')}"
                                        
                                        # Update advance payment
                                        for ap in advance_payments:
                                            if ap['id'] == advance['id']:
                                                ap['status'] = 'Completed'
                                                ap['completion_date'] = completion_datetime
                                                ap['received_amount'] = ap.get('remaining_amount', 0)
                                                ap['final_payment_method'] = payment_method
                                                ap['is_editable'] = False  # Make non-editable after completion
                                                break
                                        selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                        save_data('advance_payments.json', advance_payments, selected_hotel)
                                        
                                        # Add to respective section based on payment method
                                        if payment_method in ["Cash", "Account"]:
                                            # Add to sales
                                            sales = load_data('sales.json', selected_hotel)
                                            new_sale = {
                                                'id': generate_id(),
                                                'date': completion_datetime,
                                                'transaction_date': completion_datetime,
                                                'type': 'Advance Payment - Final',
                                                'amount': still_remaining,
                                                'payment_type': payment_method,
                                                'customer_name': advance['customer_name'],
                                                'description': f"Final payment for advance #{advance['id']} - ₹{still_remaining:,.2f} (Originally advanced: {advance['date'][:10]}, Final payment: {str(completion_date)})",
                                                'original_advance_date': advance['date'][:10],
                                                'payment_date': str(completion_date),
                                                'advance_id': advance['id'],
                                                'status': 'Completed',
                                                'created_by': st.session_state.get('username', 'Unknown')
                                            }
                                            sales.append(new_sale)
                                            save_data('sales.json', sales, selected_hotel)
                                            st.success(f"Final payment marked as received and added to {payment_method.lower()} sales!")
                                        
                                        elif payment_method == "Discount":
                                            # Add to discounts
                                            discounts = load_data('discounts.json', selected_hotel)
                                            new_discount = {
                                                'id': generate_id(),
                                                'date': completion_datetime,
                                                'customer_name': advance['customer_name'],
                                                'amount': still_remaining,
                                                'original_amount': still_remaining,
                                                'discount_type': 'Advance Payment Discount',
                                                'reason': f"Discount applied to advance payment #{advance['id']} - remaining amount waived",
                                                'reference_id': advance['id'],
                                                'percentage': 0,
                                                'original_advance_date': advance['date'][:10],
                                                'advance_id': advance['id'],
                                                'created_by': st.session_state.get('username', 'Unknown')
                                            }
                                            discounts.append(new_discount)
                                            save_data('discounts.json', discounts, selected_hotel)
                                            st.success(f"Remaining amount marked as discount and added to discount records!")
                                        
                                        elif payment_method == "Complementary":
                                            # Add to complementary records
                                            complementary_records = load_data('complementary_records.json', selected_hotel)
                                            new_comp = {
                                                'id': generate_id(),
                                                'date': completion_datetime,
                                                'customer_name': advance['customer_name'],
                                                'amount': still_remaining,
                                                'type': 'Advance Payment Complementary',
                                                'reason': f"Complementary waiver for advance payment #{advance['id']} - remaining amount waived",
                                                'reference_id': advance['id'],
                                                'original_advance_date': advance['date'][:10],
                                                'advance_id': advance['id'],
                                                'created_by': st.session_state.get('username', 'Unknown')
                                            }
                                            complementary_records.append(new_comp)
                                            save_data('complementary_records.json', complementary_records, selected_hotel)
                                            st.success(f"Remaining amount marked as complementary and added to complementary records!")
                                        
                                        st.rerun()
                
                with col2:
                    if advance['status'] in ['Pending', 'Partially Received']:
                        if st.button(f"💸 Refund", key=f"refund_{advance['id']}", help="Mark advance as refunded"):
                            for ap in advance_payments:
                                if ap['id'] == advance['id']:
                                    ap['status'] = 'Refunded'
                                    ap['refunded_date'] = get_current_datetime()
                                    break
                            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                            save_data('advance_payments.json', advance_payments, selected_hotel)
                            st.warning("Advance payment refunded!")
                            st.rerun()
                
                with col3:
                    if advance['status'] in ['Pending', 'Partially Received']:
                        if st.button(f"⏰ Mark Expired", key=f"expire_{advance['id']}", help="Mark advance as expired"):
                            for ap in advance_payments:
                                if ap['id'] == advance['id']:
                                    ap['status'] = 'Expired'
                                    ap['expired_date'] = get_current_datetime()
                                    break
                            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                            save_data('advance_payments.json', advance_payments, selected_hotel)
                            st.error("Advance payment marked as expired!")
                            st.rerun()
                
                with col4:
                    if user_role == 'Admin':
                        if st.button(f"🗑️ Delete", key=f"delete_{advance['id']}", type="secondary", help="Admin only: Delete record"):
                            advance_payments = [ap for ap in advance_payments if ap['id'] != advance['id']]
                            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                            save_data('advance_payments.json', advance_payments, selected_hotel)
                            st.success("Advance payment deleted!")
                            st.rerun()
                
                # Admin edit functionality
                if user_role == 'Admin':
                    if st.button(f"Edit Advance", key=f"edit_advance_{advance['id']}"):
                        with st.form(f"edit_advance_form_{advance['id']}"):
                            new_amount = st.number_input("Amount", value=advance['amount'], min_value=0.0)
                            new_status = st.selectbox("Status", ["Pending", "Utilized", "Refunded", "Expired"], 
                                                    index=["Pending", "Utilized", "Refunded", "Expired"].index(advance['status']))
                            new_customer = st.text_input("Customer Name", value=advance['customer_name'])
                            if st.form_submit_button("Update Advance"):
                                for ap in advance_payments:
                                    if ap['id'] == advance['id']:
                                        ap['amount'] = new_amount
                                        ap['status'] = new_status
                                        ap['customer_name'] = new_customer
                                        break
                                selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                save_data('advance_payments.json', advance_payments, selected_hotel)
                                st.success("Advance payment updated!")
                                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No advance payment records found")

# Statistics and analytics
if advance_payments:
    st.markdown("---")
    st.markdown("### Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Payment Methods:**")
        method_stats = {}
        for ap in advance_payments:
            method = ap['payment_method']
            method_stats[method] = method_stats.get(method, 0) + ap['amount']
        
        for method, amount in sorted(method_stats.items(), key=lambda x: x[1], reverse=True):
            st.write(f"• {method}: ₹{amount:,.2f}")
    
    with col2:
        st.markdown("**Status Distribution:**")
        status_stats = {}
        for ap in advance_payments:
            status = ap['status']
            status_stats[status] = status_stats.get(status, 0) + 1
        
        for status, count in status_stats.items():
            percentage = (count / len(advance_payments)) * 100
            st.write(f"• {status}: {count} ({percentage:.1f}%)")

# Pending advances summary
st.markdown("---")
st.markdown("### Advances Summary")

pending_advances_list = [ap for ap in advance_payments if ap['status'] in ['Pending', 'Partially Received']]
if pending_advances_list:
    pending_amount = sum(ap['amount'] for ap in pending_advances_list)
    st.info(f"Total pending advances: {len(pending_advances_list)} records worth ₹{pending_amount:,.2f}")
    
    # Show pending advances in a table
    pending_df = pd.DataFrame([{
        'ID': ap['id'],
        'Customer': ap['customer_name'],
        'Advance': f"₹{ap.get('advance_amount', ap.get('amount', 0)):,.2f}",
        'Remaining': f"₹{ap.get('remaining_amount', 0):,.2f}",
        'Collected': f"₹{ap.get('received_amount', 0):,.2f}",
        'Still Due': f"₹{ap.get('remaining_amount', 0) - ap.get('received_amount', 0):,.2f}",
        'Status': ap['status'],
        'Purpose': ap['purpose']
    } for ap in pending_advances_list])
    
    st.dataframe(pending_df, use_container_width=True)
else:
    st.success("No pending advances!")

# Refund management
st.markdown("---")
st.markdown("### Refund Management")

refund_advances = [ap for ap in advance_payments if ap['status'] == 'Refunded']
if refund_advances:
    total_refunded = sum(ap['amount'] for ap in refund_advances)
    st.warning(f"Total refunded: ₹{total_refunded:,.2f} across {len(refund_advances)} transactions")
else:
    st.info("No refunded advances")

# Export functionality
if user_role == 'Admin' and advance_payments:
    st.markdown("---")
    if st.button("📊 Export Advance Payments Data"):
        df = pd.DataFrame(advance_payments)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=f"advance_payments_{get_current_datetime()[:10]}.csv",
            mime="text/csv"
        )
