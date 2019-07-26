import face_recognition
import cv2

# Initialize variables
video_capture = cv2.VideoCapture(0)
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
font = cv2.FONT_HERSHEY_DUPLEX
width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)

    process_this_frame = not process_this_frame

    # Display the results
    for top, right, bottom, left in face_locations:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # calculate box size
        height = bottom - top
        width = right - left

        # draw box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)  # box around head
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)  # size: 0x0 background box
        cv2.putText(frame, "size: "+str(height)+"x"+str(width), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)  # size: 0x0 text

        # forward/back control
        cv2.rectangle(frame, (left - 1, bottom + 35), (right + 1, bottom), (255, 0, 0), cv2.FILLED)
        if (height > 250):
            cv2.putText(frame, "back up", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)
        elif (height < 200):
            cv2.putText(frame, "move forwards", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "stay put", (left + 6, bottom + 28), font, 1.0, (255, 255, 255), 1)

        # left/right control
        # BUG: the proper thresholds are unknown, so it doesn't work
        #cv2.rectangle(frame, (left - 1, bottom + 70), (right + 1, bottom + 35), (0, 255, 0), cv2.FILLED)
        #if (too far left):
        #    cv2.putText(frame, "move right", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)
        #elif (too far right):
        #    cv2.putText(frame, "move left", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)
        #else:
        #    cv2.putText(frame, "centered", (left + 6, bottom + 66), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
