import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

async def get_media_info():
    # Get the session manager
    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = manager.get_current_session()

    if session:
        info = await session.try_get_media_properties_async()
        app_name = session.source_app_user_model_id
        title = info.title
        artist = info.artist
        print(f"🎵 Now Playing: {title} - {artist} (App: {app_name})")
    else:
        print("No media is playing.")

asyncio.run(get_media_info())
