import face_recognition
import cv2
import time
import pyardrone

# Initialize face recognition variables
video_capture = cv2.VideoCapture(0)
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
font = cv2.FONT_HERSHEY_DUPLEX
width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize drone variables
drone = pyardrone.ARDrone()
drone_speed = 0.25

drone.navdata_ready.wait()  # wait until NavData is ready
drone.video_ready.wait()  # wait until video is ready

drone.takeoff()  # take off and await further instruction

try:
    while True:
        # Grab a single frame of video
        frame = drone.video_client.frame

        #Resize frame of video to 1/2 size for faster face recognition processing
        #small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        #rgb_small_frame = small_frame[:, :, ::-1]
        frame = frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(frame) #instead of small frame

        process_this_frame = not process_this_frame

        # Parse image if face detected
        if len(face_locations) > 0:
            # Get edges of face's bounding box
            top = face_locations[0][0]
            right = face_locations[0][1]
            bottom = face_locations[0][2]
            left = face_locations[0][3]

            # Scale back up face locations since the frame we detected in was scaled to 1/2 size
            #top *= 2
            #right *= 2
            #bottom *= 2
            #left *= 2

            # calculate box size
            height = bottom - top
            width = right - left

            # draw box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # box around head
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)  # size: 0x0 background box
            cv2.putText(frame, "size: "+str(height)+"x"+str(width), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)  # size: 0x0 text

            # forward/back control
            cv2.rectangle(frame, (left - 1, bottom + 35), (right + 1, bottom), (255, 0, 0), cv2.FILLED)
            if (height > 100):
                cv2.putText(frame, "back up", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)
                drone.move(backward=drone_speed)
            elif (height < 75):
                cv2.putText(frame, "move forwards", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)
                drone.move(forward=drone_speed)
            else:
                cv2.putText(frame, "stay put", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)

            # rotation control
            cv2.rectangle(frame, (left - 1, bottom + 70), (right + 1, bottom + 35), (0, 255, 0), cv2.FILLED)
            if (left < 160):
                cv2.putText(frame, "rotate left", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)
                drone.move(ccw=drone_speed)
            elif (right > 480):
                cv2.putText(frame, "rotate right", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)
                drone.move(cw=drone_speed)
            else:
                cv2.putText(frame, "centered", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)

            # up/down control
            cv2.rectangle(frame, (left - 1, bottom + 105), (right + 1, bottom + 70), (0, 0, 255), cv2.FILLED)
            if (top < 180):
                cv2.putText(frame, "move up", (left + 6, bottom + 99), font, 1.0, (255, 255, 255), 1)
                drone.move(up=drone_speed)
            elif (bottom > 180):
                cv2.putText(frame, "move down", (left + 6, bottom + 99), font, 1.0, (255, 255, 255), 1)
                drone.move(down=drone_speed)
            else:
                cv2.putText(frame, "centered", (left + 6, bottom + 99), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'l' for immediate landing
        if cv2.waitKey(1) & 0xFF == ord('l'):
            drone.land()
            break
        # Hit 'e' for "emergency" panic to get it out of a tree, etc.
        if cv2.waitKey(1) & 0xFF == ord('e'):
            drone.emergency()
except Exception as e:
    print("There was a problem:", str(e))
finally:
    print("Landing drone.")
    drone.land()

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()