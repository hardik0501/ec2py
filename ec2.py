import cv2
from cvzone.HandTrackingModule import HandDetector
import boto3
import time

# Initialize webcam and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1, detectionCon=0.8)

# AWS setup
ec2 = boto3.resource('ec2', region_name='us-east-1')  # Change region if needed
KEY_NAME = 'your-keypair-name'  # 🔐 Replace with your actual EC2 Key Pair Name
AMI_ID = 'ami-0c02fb55956c7d316'  # ✅ Amazon Linux 2 AMI for us-east-1
INSTANCE_TYPE = 't2.micro'

last_launched_time = 0

def launch_ec2_instance():
    print("🚀 Launching EC2 instance...")
    instance = ec2.create_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME
    )[0]

    print(f"Waiting for EC2 Instance {instance.id} to start...")
    instance.wait_until_running()
    instance.load()
    print(f"✅ EC2 Instance Running at: {instance.public_dns_name} (ID: {instance.id})")
    return instance.id

# Main loop
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        fingers = detector.fingersUp(hands[0])
        count = fingers.count(1)

        cv2.putText(img, f'Fingers: {count}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 255, 0), 3)

        # Launch EC2 when exactly 1 finger is shown and 10 sec cooldown passed
        if count == 1 and (time.time() - last_launched_time > 10):
            instance_id = launch_ec2_instance()
            print(f"🎉 Instance Launched: {instance_id}")
            last_launched_time = time.time()

    cv2.imshow("Gesture2EC2 - Show 1 Finger to Launch EC2", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
