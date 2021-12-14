import os




if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    os.environ['SCHEMES_PATH'] = '/home/rost/Development/GIS_OK/schemes/schemes'

    uvicorn.run('src.service.wsgi:app', host="0.0.0.0", port=8081, log_level="debug")