from scripbox import api

def login(mobile_number):
    try:
        success = api.login_api(mobile_number)
        if not success:
            print("❌ Could not send OTP.")
            return

        otp = input("Enter the OTP received: ")
        verified = api.verify_otp_api(mobile_number, otp)

        if not verified:
            print("❌ Login failed. OTP might be incorrect or expired.")
        # If verified, success message already printed inside the function

    except Exception as e:
        print("❌ Login failed:", str(e))

def logout(): 
   if api.delete_token():
       print("🚪logout successfull")
   else:
       print("ℹ️No login found")
      
