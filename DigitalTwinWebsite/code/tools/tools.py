from flask import url_for


def generate_iframe(project_name):
    try:
        # Manually constructing the URL with correct encoding for spaces
        base_url = url_for('static', filename='Unity/ViewerBuild/index.html', _external=True)
        # Use urllib.parse.quote to encode the project_name properly, replacing spaces with %20
        from urllib.parse import quote
        encoded_project_name = quote(project_name)  # Encodes spaces as %20
        viewer_url = f"{base_url}?projectName={encoded_project_name}"
        iframe_code = f'<iframe src="{viewer_url}" width="800" height="600"></iframe>'
        return 200, iframe_code
    except Exception as e:
        return 500, None
    