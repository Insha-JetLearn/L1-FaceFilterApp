import os
import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
from filters import FILTERS

app = Flask(__name__)

# Load the cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_frame():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
            
        filter_name = data.get('filter', None)
        
        # Decode base64 image
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Mirror flip if needed (usually handled by frontend, but just in case)
        # We assume frontend sends the canvas as displayed
        
        # If no filter selected, return original
        if not filter_name or filter_name not in FILTERS:
            _, buffer = cv2.imencode('.jpg', frame)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            return jsonify({'image': f'data:image/jpeg;base64,{encoded_img}'})
            
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        
        # Apply filter to each face
        # For simplicity and performance, some filters might apply to the whole frame
        # We pass the largest face to filters that expect a single face, or loop
        if len(faces) > 0:
            # Sort by size to prioritize main face, though we can process all
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            
            # Apply to the largest face for most filters, some handle multiple
            if filter_name in ['vintage', 'sketch', 'mirror', 'cyberpunk']:
                # These often apply to the whole frame but can use face data
                frame = FILTERS[filter_name](frame, faces[0])
            else:
                for face in faces:
                    frame = FILTERS[filter_name](frame, face)
        else:
            # If no face detected, some filters can still apply (vintage, sketch, mirror)
            if filter_name in ['vintage', 'sketch', 'mirror', 'cyberpunk']:
                # Pass a dummy rect (0,0,0,0) or full frame rect
                dummy_rect = (0, 0, frame.shape[1], frame.shape[0])
                frame = FILTERS[filter_name](frame, dummy_rect)

        # Encode back to base64
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({'image': f'data:image/jpeg;base64,{encoded_img}'})

    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use standard port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
