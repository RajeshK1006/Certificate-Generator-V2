Cultural Event Management System.
================================

Table of Contents
-----------------

*   [Project Description](#project-description)
    
*   [Features](#features)
    
*   [Technologies Used](#technologies-used)
    
*   [Installation](#installation)
    
*   [Usage](#usage)
    
*   [Contributing](#contributing)
    
*   [License](#license)
    

Project Description
-------------------

The Cultural Event Management System is a web application designed to manage cultural events and participants. It allows administrators to register participants, upload event details and certificate templates, and generate certificates for participants. Participants can view their event participation details and download certificates.

Features
--------

*   User registration and login.
    
*   Admin dashboard for managing events and participants.
    
*   Upload participant lists and certificate templates.
    
*   Generate and download participation certificates.
    
*   User dashboard to view participation details.
    

Technologies Used
-----------------

*   **Backend**: Flask, Firebase Authentication, Firestore, Firebase Storage
    
*   **Frontend**: HTML, CSS, JavaScript
    
*   **Libraries**: pandas, requests, PIL (Python Imaging Library)
    
*   **Other Tools**: Firebase Admin SDK
    

Installation
------------

### Prerequisites

*   Python 3.6+
    
*   Firebase account with a service account key
    

### Steps

1.  sh- code : git clone Repo URL
    
2.  sh- code: python3 -m venv venvsource venv/bin/activate # On Windows: venv\\Scripts\\activate
    
3.  sh- code: pip install -r requirements.txt
    
4.  **Add your Firebase service account key:**Place your serviceKey.json file in the project root directory.
    
5.  sh- code: flask run
    

Usage
-----

### Admin

1.  **Login**: Use the admin email to login.
    
2.  **Admin Dashboard**: Upload participant lists and certificate templates, and view all events and participants.
    
3.  **Generate Certificates**: Automatically generate and provide download links for participant certificates.
    

### Participant

1.  **Register**: Sign up with your email.
    
2.  **Login**: Login to view your event participation details.
    
3.  **Download Certificates**: Download your participation certificates from the dashboard.
    

Contributing
------------

We welcome contributions! Please follow these steps:

1.  Fork the repository.
    
2.  Create a new branch: git checkout -b feature-name.
    
3.  Make your changes and commit them: git commit -m 'Add some feature'.
    
4.  Push to the branch: git push origin feature-name.
    
5.  Open a pull request.
    

License
-------

This project is licensed under the MIT License.
