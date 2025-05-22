import asyncio
import os
import aiohttp
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from dotenv import load_dotenv
from loguru import logger
import uuid

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Store user search results
user_search_results = {}

async def cleanup_previous_search(user_id):
    """Очищает предыдущие результаты поиска"""
    if user_id in user_search_results:
        try:
            del user_search_results[user_id]
        except Exception as e:
            pass  # Полностью убираем логирование

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await cleanup_previous_search(message.from_user.id)
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"<b>🎵 Добро пожаловать в HX Music Bot, {user_name}!</b>\n\n"
        "✨ <b>Твой персональный музыкальный гид</b> ✨\n\n"
        "<b>Возможности бота:</b>\n"
        "   🎧 Поиск треков по названию\n"
        "   🔥 Топ популярных композиций\n"
        "   ⚡ Мгновенная загрузка в высоком качестве\n\n"
        "🌈 <b>Как использовать:</b>\n"
        "1. Отправь название трека или исполнителя\n"
        "2. Выбери нужный вариант из списка\n"
        "3. Получи файл за секунды!\n\n"
        "Для начала просто введи название трека в чат!"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="💬 Поддержка",
            url="https://t.me/hexsad01"
        )
    )
    
    await message.answer(
        text=welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup()
    )

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    await cleanup_previous_search(message.from_user.id)
    search_id = str(uuid.uuid4())  # Генерируем уникальный ID
    
    # Отправляем сообщение "Загружаю популярные треки..."
    search_message = await message.answer("🔍 Ищу популярные треки...")
    
    try:
        async with aiohttp.ClientSession() as session:
            client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
            if not client_id:
                await search_message.edit_text("⚠️ Ошибка: Отсутствует SoundCloud API ключ.")
                return
                
            # SoundCloud Charts API
            url = f"https://api-v2.soundcloud.com/charts?kind=top&genre=soundcloud:genres:all-music&limit=100&client_id={client_id}"
            
            async with session.get(url) as response:
                if response.status != 200:
                    await search_message.edit_text(f"⚠️ Ошибка при загрузке топа: {response.status}")
                    return
                    
                data = await response.json()
                tracks = [item["track"] for item in data.get("collection", []) if "track" in item]
                
                if not tracks:
                    await search_message.edit_text("😕 Не удалось загрузить топ треков")
                    return
                
                # Store results
                user_search_results[search_id] = {
                    "tracks": tracks,
                    "current_page": 1,
                    "query": "🔥 Топ треков",
                    "message_id": search_message.message_id,
                    "chat_id": search_message.chat.id,
                    "user_id": message.from_user.id
                }
                
                await show_tracks_page(search_id, 1)
                
    except Exception as e:
        logger.error(f"Ошибка при загрузке топа: {e}")
        await search_message.edit_text(f"⚠️ Произошла ошибка: {e}")

@dp.message(F.text & ~F.command)
async def search_track(message: types.Message):
    await cleanup_previous_search(message.from_user.id)
    search_id = str(uuid.uuid4())
    
    query = message.text.strip()
    if not query:
        await message.answer("Пожалуйста, введите название песни для поиска.")
        return
    
    # Отправляем сообщение "Ищу..." и сохраняем его для последующего редактирования
    search_message = await message.answer(f"🔍 Ищу '{query}'...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # SoundCloud API client ID (you'll need to get your own)
            client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
            if not client_id:
                await search_message.edit_text("⚠️ Ошибка: Отсутствует SoundCloud API ключ.")
                return
                
            # Search tracks via SoundCloud API
            url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={client_id}&limit=100"
            
            async with session.get(url) as response:
                if response.status != 200:
                    await search_message.edit_text(f"⚠️ Ошибка при поиске: {response.status}")
                    return
                    
                data = await response.json()
                tracks = data.get("collection", [])
                
                if not tracks:
                    await search_message.edit_text("😕 Ничего не найдено. Попробуйте другой запрос.")
                    return
                
                # Store results for this user
                user_search_results[search_id] = {
                    "tracks": tracks,
                    "current_page": 1,
                    "query": query,
                    "message_id": search_message.message_id,
                    "chat_id": search_message.chat.id,
                    "user_id": message.from_user.id
                }
                
                # Show first page of results (в том же сообщении)
                await show_tracks_page(search_id, 1)
                
    except Exception as e:
        logger.error(f"Ошибка при поиске треков: {e}")
        await search_message.edit_text(f"⚠️ Произошла ошибка при поиске: {e}")

async def show_tracks_page(search_id, page):
    if search_id not in user_search_results:
        return
        
    results = user_search_results[search_id]
    tracks = results["tracks"]
    query = results["query"]
    chat_id = results["chat_id"]
    message_id = results["message_id"]
    
    results["current_page"] = page
    
    tracks_per_page = 10
    start_idx = (page - 1) * tracks_per_page
    end_idx = min(start_idx + tracks_per_page, len(tracks))
    
    total_pages = (len(tracks) + tracks_per_page - 1) // tracks_per_page
    
    # Формируем заголовок без приписки "Поиск:" для похожих треков
    if query.startswith("Похожие на") or query == "🔥 Топ треков":
        message_text = f"<b>{query}</b>\n\n"
    else:
        message_text = f"🎵 <b>Поиск:</b> {query}\n\n"
    
    for i in range(start_idx, end_idx):
        track = tracks[i]
        track_number = i - start_idx + 1
        title = track.get("title", "Без названия").replace("<", "&lt;").replace(">", "&gt;")
        artist = track.get("user", {}).get("username", "Неизвестный").replace("<", "&lt;").replace(">", "&gt;")
        duration_ms = track.get("duration", 0)
        duration_sec = duration_ms // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        
        message_text += f"{track_number}. <b>{artist}</b> - {title} [{minutes}:{seconds:02d}]\n"
    
    # Create inline keyboard
    builder = InlineKeyboardBuilder()
    
    # Track selection buttons (1-10) в один ряд по 5 кнопок
    current_row = []
    for i in range(start_idx, end_idx):
        track_number = i - start_idx + 1  # Номер в текущей странице (1-10)
        current_row.append(types.InlineKeyboardButton(
            text=str(track_number),
            callback_data=f"track_{search_id}_{i}"
        ))
        
        # Create a new row after every 5 buttons
        if len(current_row) == 5:
            builder.row(*current_row)
            current_row = []
    
    # Add any remaining buttons
    if current_row:
        builder.row(*current_row)
    
    # Navigation buttons с нумерацией страниц
    nav_buttons = []
    
    # Previous page button
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton(
            text="⬅️",
            callback_data=f"page_{search_id}_{page-1}"
        ))
    
    # Page number indicator
    nav_buttons.append(types.InlineKeyboardButton(
        text=f"📄 {page}/{total_pages}",
        callback_data=f"noop"  # Эта кнопка ничего не делает
    ))
    
    # Next page button
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton(
            text="➡️",
            callback_data=f"page_{search_id}_{page+1}"
        ))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Редактируем существующее сообщение вместо отправки нового
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")

async def get_track_stream_url(track_id, client_id):
    """Получает прямую ссылку на аудиофайл трека"""
    try:
        async with aiohttp.ClientSession() as session:
            # Попытка 1: Progressive download через веб-API (предпочтительный метод)
            track_url = f"https://api-v2.soundcloud.com/tracks/{track_id}?client_id={client_id}"
            logger.info(f"Пробуем веб API: {track_url}")
            
            async with session.get(track_url) as response:
                if response.status == 200:
                    track_data = await response.json()
                    logger.info("Информация о треке получена успешно")
                    
                    # Проверяем media transcoding
                    if "media" in track_data and "transcodings" in track_data["media"]:
                        transcodings = track_data["media"]["transcodings"]
                        logger.info(f"Найдено {len(transcodings)} вариантов кодировки")
                        
                        # Сначала ищем progressive формат
                        for t in transcodings:
                            protocol = t.get("format", {}).get("protocol")
                            mime_type = t.get("format", {}).get("mime_type")
                            
                            if protocol == 'progressive':
                                logger.info(f"Найден progressive формат: {mime_type}")
                                stream_url = t.get("url")
                                if stream_url:
                                    async with session.get(f"{stream_url}?client_id={client_id}") as stream_response:
                                        if stream_response.status == 200:
                                            stream_data = await stream_response.json()
                                            return stream_data.get("url")
                        
                        # Если progressive не найден, пробуем HLS
                        for t in transcodings:
                            protocol = t.get("format", {}).get("protocol")
                            mime_type = t.get("format", {}).get("mime_type")
                            
                            if protocol in ['hls', 'hls_secure']:
                                logger.info(f"Найден HLS формат: {mime_type}")
                                stream_url = t.get("url")
                                if stream_url:
                                    async with session.get(f"{stream_url}?client_id={client_id}") as stream_response:
                                        if stream_response.status == 200:
                                            stream_data = await stream_response.json()
                                            return stream_data.get("url")

            # Попытка 2: Мобильный API как запасной вариант
            mobile_url = f"https://api-mobi.soundcloud.com/tracks/{track_id}?client_id={client_id}"
            logger.info(f"Пробуем мобильный API: {mobile_url}")
            
            async with session.get(mobile_url) as response:
                if response.status == 200:
                    data = await response.json()
                    stream_url = data.get('stream_url')
                    if stream_url:
                        full_url = f"{stream_url}?client_id={client_id}"
                        async with session.get(full_url, allow_redirects=True) as audio_response:
                            if audio_response.status == 200:
                                return str(audio_response.url)

    except Exception as e:
        logger.error(f"Ошибка при получении URL потока: {e}")
    
    logger.error("Все попытки получить URL потока не удались")
    return None

async def download_audio(url):
    """Скачивает аудио по URL"""
    try:
        timeout = aiohttp.ClientTimeout(total=300)  # 5 минут таймаут
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"Начинаю загрузку аудио с URL: {url}")
            
            # Проверяем, является ли URL HLS плейлистом
            if '.m3u8' in url:
                logger.info("Обнаружен HLS поток, загружаю плейлист")
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Не удалось получить HLS плейлист. Статус: {response.status}")
                        return None
                        
                    playlist = await response.text()
                    segments = []
                    total_size = 0
                    
                    # Собираем все сегменты из плейлиста
                    for line in playlist.split('\n'):
                        if line.startswith('http') and ('.mp3' in line or '.aac' in line or '.ts' in line):
                            segments.append(line)
                    
                    if not segments:
                        logger.error("Не найдены аудио сегменты в HLS плейлисте")
                        return None
                    
                    logger.info(f"Найдено {len(segments)} сегментов для загрузки")
                    all_data = bytearray()
                    
                    # Скачиваем все сегменты
                    for i, segment_url in enumerate(segments, 1):
                        logger.info(f"Загрузка сегмента {i}/{len(segments)}")
                        try:
                            async with session.get(segment_url) as segment_response:
                                if segment_response.status == 200:
                                    segment_data = await segment_response.read()
                                    all_data.extend(segment_data)
                                    total_size += len(segment_data)
                                    logger.info(f"Сегмент {i} загружен: {len(segment_data)} байт")
                                else:
                                    logger.error(f"Не удалось загрузить сегмент {i}. Статус: {segment_response.status}")
                        except Exception as e:
                            logger.error(f"Ошибка при загрузке сегмента {i}: {e}")
                            continue
                    
                    if total_size < 100 * 1024:  # Меньше 100 KB
                        logger.error(f"Общий размер загрузки слишком мал: {total_size} байт")
                        return None
                        
                    logger.info(f"Успешно загружены все сегменты. Общий размер: {total_size / (1024*1024):.2f} МБ")
                    return bytes(all_data)
            
            # Для обычных URL (не HLS)
            logger.info(f"Загрузка аудио с: {url}")
            async with session.get(url) as response:
                if response.status == 200:
                    # Проверяем размер файла
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        logger.info(f"Ожидаемый размер файла: {size_mb:.2f} МБ")
                        if size_mb < 0.1:  # Меньше 100 KB
                            logger.error("Размер файла слишком мал")
                            return None
                    
                    data = await response.read()
                    file_size = len(data) / (1024 * 1024)
                    logger.info(f"Загрузка завершена. Размер файла: {file_size:.2f} МБ")
                    
                    if len(data) < 100 * 1024:  # Меньше 100 KB
                        logger.error("Загруженный файл слишком мал")
                        return None
                        
                    return data
                else:
                    logger.error(f"Не удалось загрузить аудио. Статус: {response.status}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке аудио: {e}")
    return None

@dp.callback_query(F.data.startswith("track_"))
async def process_track_selection(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    search_id = parts[1]
    track_idx = int(parts[2])
    
    if search_id not in user_search_results:
        await callback.answer("Результаты поиска устарели", show_alert=True)
        return
        
    results = user_search_results[search_id]
    
    if results["user_id"] != callback.from_user.id:
        await callback.answer("Это не ваш поиск!", show_alert=True)
        return
        
    tracks = results["tracks"]
    query = results["query"]
    chat_id = results["chat_id"]
    message_id = results["message_id"]
    
    if track_idx >= len(tracks):
        await callback.answer("Трек не найден.", show_alert=True)
        return
    
    # Уведомление о скачивании в inline режиме
    await callback.answer("Загружаю трек...")
    
    # Редактируем сообщение с результатами, добавляя информацию о загрузке
    selected_track = tracks[track_idx]
    track_title = selected_track.get("title", "Без названия")
    artist = selected_track.get("user", {}).get("username", "Неизвестный исполнитель")
    
    # Сохраняем текущую страницу
    current_page = results["current_page"]
    
    # Обновляем сообщение статусом загрузки
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"⏳ <b>Загрузка трека:</b>\n<i>{artist} - {track_title}</i>...",
        reply_markup=None,
        parse_mode=ParseMode.HTML
    )
        
    try:
        track_id = selected_track.get("id")
        artwork_url = selected_track.get("artwork_url", "")
        permalink_url = selected_track.get("permalink_url", "")
        
        logger.info(f"Обработка трека: {track_title} от {artist} (ID: {track_id})")
        
        # Если есть artwork_url, получаем версию большего размера
        if artwork_url:
            artwork_url = artwork_url.replace("-large", "-t500x500")
        
        # Получаем ссылку на аудиопоток
        client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
        if not client_id:
            logger.error("Не найден SoundCloud client ID")
            raise ValueError("Отсутствует SoundCloud client ID")
            
        stream_url = await get_track_stream_url(track_id, client_id)
        
        if not stream_url:
            logger.error("Не удалось получить URL потока")
            # Восстанавливаем поисковые результаты при ошибке
            await show_tracks_page(search_id, current_page)
            await callback.answer("❌ Не удалось получить ссылку на аудио", show_alert=True)
            return
        
        # Скачиваем аудио
        audio_data = await download_audio(stream_url)
        
        if not audio_data:
            logger.error("Не удалось загрузить аудио данные")
            # Восстанавливаем поисковые результаты при ошибке
            await show_tracks_page(search_id, current_page)
            await callback.answer("❌ Не удалось скачать аудио", show_alert=True)
            return
        
        logger.info("Создание аудио файла для отправки")
        # Создаем BufferedInputFile для отправки аудио
        audio_file = BufferedInputFile(
            audio_data,
            filename=f"{track_title}.mp3"
        )
        
        # Отправляем аудио сообщение с метаданными
        caption = (f"👉 <a href='https://t.me/hxmusic_robot'>Ищи свои любимые треки в боте</a> 👈")
        
        # Если есть обложка, скачиваем и ее
        thumbnail = None
        if artwork_url:
            try:
                logger.info("Загрузка обложки")
                # Пробуем скачать обложку
                async with aiohttp.ClientSession() as session:
                    async with session.get(artwork_url) as response:
                        if response.status == 200:
                            thumbnail_data = await response.read()
                            thumbnail = BufferedInputFile(
                                thumbnail_data,
                                filename="thumbnail.jpg"
                            )
                            logger.info("Обложка успешно загружена")
            except Exception as e:
                logger.error(f"Не удалось загрузить обложку: {e}")
                # Если не получилось скачать обложку, продолжаем без нее
                pass
        
        # Создаем клавиатуру для кнопки "Найти похожие"
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text="🔍 Найти похожие",
                callback_data=f"similar_{track_id}"
            )
        )
        
        logger.info("Отправка аудио сообщения")
        # Отправляем файл с метаданными
        await callback.message.answer_audio(
            audio=audio_file,
            caption=caption,
            title=f"{track_title} | tg: hxmusic_robot",
            performer=artist,
            thumbnail=thumbnail,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        
        logger.info("Аудио успешно отправлено")
        # Удаляем сообщение с результатами поиска
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке трека: {str(e)}")
        # Восстанавливаем поисковые результаты при ошибке
        await show_tracks_page(search_id, current_page)
        await callback.answer(f"❌ Ошибка при загрузке трека", show_alert=True)

@dp.callback_query(F.data.startswith("page_"))
async def process_page_navigation(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    search_id = parts[1]
    page = int(parts[2])
    
    if search_id not in user_search_results:
        await callback.answer("Результаты поиска устарели", show_alert=True)
        return
    
    # Показываем новую страницу (редактируя существующее сообщение)
    await show_tracks_page(search_id, page)
    await callback.answer()

# Обработчик для кнопки с номером страницы (которая ничего не делает)
@dp.callback_query(F.data == "noop")
async def process_noop(callback: types.CallbackQuery):
    await callback.answer("Текущая страница")

@dp.callback_query(F.data.startswith("similar_"))
async def find_similar_tracks(callback: types.CallbackQuery):
    track_id = callback.data.split("_")[1]
    search_id = str(uuid.uuid4())
    
    # Отправляем сообщение о начале поиска
    search_message = await callback.message.answer("🔍 Ищу похожие треки...")
    
    try:
        async with aiohttp.ClientSession() as session:
            client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
            if not client_id:
                await search_message.edit_text("⚠️ Ошибка: Отсутствует SoundCloud API ключ.")
                return

            # API для получения похожих треков
            url = f"https://api-v2.soundcloud.com/tracks/{track_id}/related?client_id={client_id}&limit=100"
            
            async with session.get(url) as response:
                if response.status != 200:
                    await search_message.edit_text(f"⚠️ Ошибка при поиске: {response.status}")
                    return
                    
                data = await response.json()
                tracks = data.get("collection", [])
                
                if not tracks:
                    await search_message.edit_text("😕 Похожих треков не найдено")
                    return
                
                # Сохраняем результаты
                user_search_results[search_id] = {
                    "tracks": tracks,
                    "current_page": 1,
                    "query": f"Похожие на {callback.message.audio.title}",
                    "message_id": search_message.message_id,
                    "chat_id": search_message.chat.id,
                    "user_id": callback.from_user.id
                }
                
                await show_tracks_page(search_id, 1)
                
    except Exception as e:
        logger.error(f"Ошибка при поиске похожих треков: {e}")
        await search_message.edit_text(f"⚠️ Произошла ошибка: {e}")
    await callback.answer()

async def main():
    logger.info("Бот запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот останавливается...")
        await bot.session.close()
        await dp.storage.close()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Бот успешно остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass 