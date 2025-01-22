# Music Albums Cover Gallery

Music Albums Cover Gallery is a web application that allows users to share and discover album covers in their original 1920x1920 pixel format. It provides a simple, clean interface for uploading and viewing album artwork while maintaining high-quality standards.

![Screenshot](https://raw.githubusercontent.com/ufuayk/music-albums-cover-gallery/main/screenshot.png)

## Features

- **High-Quality Album Covers**: Strict 1920x1920 pixel requirement ensures consistent quality.
- **User-Friendly Interface**: Simple and intuitive design for easy navigation.
- **Rate Limiting**: Built-in protection against abuse.
- **Admin Panel**: Secure administration interface for content moderation.
- **Responsive Design**: Works seamlessly on both desktop and mobile devices.

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Image Processing**: Pillow (PIL)
- **Security**: Flask-Limiter
- **Environment Variables**: python-dotenv
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ufuayk/music-albums-cover-gallery.git
cd music-albums-cover-gallery
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with the following content:
```
ADMIN_PASSWORD=your_secure_password_here
```

5. Initialize the database:
```bash
python app.py
```

## Usage

### For Users
1. Visit the homepage
2. Select an album cover image (must be 1920x1920 pixels)
3. Enter artist name and album name
4. Click upload
5. View your uploaded cover in the gallery

### For Administrators
1. Access `/admin/login`
2. Enter your admin password
3. Manage uploaded content through the admin panel
4. Delete inappropriate content as needed

## Rate Limiting 🚦

- Regular uploads: 2 per hour
- API access: 200 requests per day, 100 per hour
- General endpoints: 5 requests per minute

Rate limiting can be disabled by creating a `.env-limit` file with content `false`.

## Security Features

- Admin authentication required for sensitive operations
- Rate limiting to prevent abuse
- File size restrictions (max 4MB)
- Secure session management
- Input validation and sanitization

## Directory Structure

```
music-albums-cover-gallery/
├── app.py              
├── requirements.txt   
├── .env               
├── .env-limit         
├── albums.db          
├── static/
│   ├── covers/        
│   └── img/           
└── templates/
    ├── main.html      
    ├── admin_login.html
    └── admin_panel.html
```

## Deployment

The application is designed to be deployed on Python Anywhere:

1. Create a Python Anywhere account
2. Upload the project files
3. Set up a virtual environment
4. Configure the WSGI file
5. Set up static files directory
6. Create necessary environment variables

For detailed deployment instructions, please refer to the deployment guide.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
