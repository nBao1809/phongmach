from twilio.rest import Client

# twilio
# recover code SXLP2CKHGF4ZVSZPJ3F8P6KW
def sendSMS(number, message):
    client = Client(account_sid, auth_token)

    from_number = '+12314272404'
    if number.startswith('0'):
        # Cắt số 0 ở đầu và thêm +84
        formatted_number = '+84' + number[1:]
    else:
        # Nếu số điện thoại đã có định dạng quốc tế, chỉ cần thêm + nếu chưa có
        if not number.startswith('+'):
            formatted_number = '+84' + number
        else:
            formatted_number = number
    # Gửi SMS
    try:
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=formatted_number
        )
        return {'success': True, 'sid': message.sid}
    except Exception as e:
        return {'error': str(e),'number': formatted_number}
