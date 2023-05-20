import launch

if not launch.is_installed("qrcode"):
    launch.run_pip("install qrcode==7.4.2", "requirements for generating QR codes")
