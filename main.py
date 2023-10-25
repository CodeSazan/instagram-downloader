import re , requests , random , os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from db import *

bot = Client(
    name = session_name, 
    api_id = api_id,
    api_hash = api_hash,
    bot_token = bot_token
)
 

try:
    os.system("clear")
except:
    os.system("cls")

print('Bot is Running ...')

async def is_member(chat, user):
    try:
        member = await bot.get_chat_member(chat, user)
        return True
    except Exception as e:
        return False

@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    
    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]

    if user_id in admins or bot_setting != "off":
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
            db.commit()

        cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
        ban_status = cursor.fetchone()[0]
        if ban_status == 'yes':
            await message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        else:
            await message.reply('<b>🖐با سلام\n\n❤️به ربات دانلود از اینستاگرام خوش اومدی</b>', quote=True)

    elif bot_setting == "off":
        await message.reply("<b>ربات خاموش است</b>", quote=True)


@bot.on_callback_query(filters.regex(r"Join"))
async def join_callback(client, callback_query):
    data = callback_query.data
    if data == "Join":
        user_id = callback_query.from_user.id
        if not await is_member(f"@{channel}", user_id):
            await callback_query.answer("شما هنوز عضو کانال نیستید", show_alert=True)
        else:
            await callback_query.message.reply('<b>🖐با سلام\n\n❤️به ربات دانلود از اینستاگرام خوش اومدی</b>', quote=True)

@bot.on_message(filters.regex(r"(instagram\.com/reel/|instagram\.com/p/)") & filters.private)
async def instagram_post(client, message):

    user_id = message.from_user.id
    
    cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
    ban_status = cursor.fetchone()[0]

    if ban_status == 'yes':
        await message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        return

    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]
    
    if bot_setting == "off":
        await message.reply("<b>ربات خاموش است</b>", quote=True)
        return

    if not await is_member(f"@{channel}", user_id):
        reply_markup = [
            [InlineKeyboardButton("🔐 | عضویت در کانال", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton('✅ | عضو شدم •', callback_data="Join")]
        ]
        await message.reply('کاربر گرامی، برای استفاده از ربات ابتدا در کانال زیر عضو شوید 👇', reply_markup=InlineKeyboardMarkup(reply_markup), quote=True)
    else:
        url = message.text
        api = f"{web_url}?key={api_key}&type=postdownloader&link={url}"
        sent_message = await message.reply('<b>🔍 در حال دریافت اطلاعات پست...</b>', quote=True)
        response = requests.get(api)
        data = response.json()

        if data['status'] == 455:
            await sent_message.edit_text('<b>♻️ اطلاعات پست یافت نشد</b>')
            return

        Number = len(data['result']['medias'])
        await sent_message.edit_text(f"<b>🔱 لطفا صبر کنید\n🗂 تعداد عکس و فیلم ها: {Number}</b>")

        for i in range(Number):
            II = i + 1
            url = data['result']['medias'][i]['url']
            extension = data['result']['medias'][i]['extension']
            caption = f"<b>({II}/{Number})\n🤖 ارسال شده توسط : @{id_bot}</b>"
            if extension == 'jpg' or extension == 'webp':
                await message.reply_photo(url, caption=caption, quote=True)
            elif extension == 'mp4':
                response = requests.head(url)
                video_size = int(response.headers.get('content-length', 0))

                if video_size < 20970000:
                    await message.reply_video(url, caption=caption, quote=True)
                else:
                    response = requests.get(url)
                    rand = random.randint(1000, 9999999)
                    file_name = f"video-{rand}.mp4"
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    await message.reply_video(file_name, caption=caption, quote=True)
                    os.remove(file_name)


@bot.on_message(filters.regex(r'^@') & filters.private)
async def get_instagram_info(client, message):
    user_id = message.from_user.id
    
    cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
    ban_status = cursor.fetchone()[0]

    if ban_status == 'yes':
        await message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        return

    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]
    
    if bot_setting == "off":
        await message.reply("<b>ربات خاموش است</b>", quote=True)
        return
    
    if not await is_member(f"@{channel}", user_id):
        reply_markup = [
            [InlineKeyboardButton("🔐 | عضویت در کانال", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton('✅ | عضو شدم •', callback_data="Join")]
        ]
        await message.reply('کاربر گرامی، برای استفاده از ربات ابتدا در کانال زیر عضو شوید 👇', reply_markup=InlineKeyboardMarkup(reply_markup), quote=True)
    else:
        text = message.text
        username = text.lstrip('@')
        info_url = f"{web_url}?key={api_key}&type=instainfo&username={username}"
        sent_message = await message.reply('<b>🔍 در حال دریافت اطلاعات...</b>', quote=True)
        response = requests.get(info_url)
        data = response.json()

        if data['status'] == 450:
            await sent_message.edit('♻️ پیج مورد نظر پیدا نشد')
            return

        if data["status"] == 200:
            result = data["result"][0]
            id = result['Id']
            name = result['name']
            bio = result['bio']
            username = result['username']
            followers = result['followers']
            following = result['following']
            post_count = result['post_count']
            is_verified = result['is_verified']
            is_private = result['is_private']
            profile = result['profile']

            private_no = [
                [InlineKeyboardButton('🎥 دانلود استوری 📸', callback_data=f"pagestory|{username}")],
                [InlineKeyboardButton('💫 دانلود هایلایت', callback_data=f"pagehightlight|{username}")],
            ]
            private_yes = [
                [InlineKeyboardButton('پیج شخصی میباشد', callback_data="0000000000")],
            ]

            response_text = f"🆔 ID : <code>{id}</code>\n\n🖊 Name : <code>{name}</code>\n\n✉️ Username : <code>{username}</code>\n\n🔖 Bio :\n\n<code>{bio}</code>\n\n🔍 Follower Count : <code>{followers}</code>\n\n🔎 Following Count : <code>{following}</code>\n\n📝 Post Count : <code>{post_count}</code>\n\n🔵 Blue tick : <code>{is_verified}</code>\n\n🔒 Is Private : <code>{is_private}</code>"

            if profile is None:
                if is_private == '❌':
                    await message.reply(response_text, reply_markup=InlineKeyboardMarkup(private_no), quote=True)
                else:
                    await message.reply(response_text, reply_markup=InlineKeyboardMarkup(private_yes), quote=True)
            else:
                if is_private == '❌':
                    await message.reply_photo(photo=profile, caption=response_text, reply_markup=InlineKeyboardMarkup(private_no), quote=True)
                else:
                    await message.reply_photo(photo=profile, caption=response_text, reply_markup=InlineKeyboardMarkup(private_yes), quote=True)


@bot.on_callback_query(filters.regex(r"pagestory\|"))
async def page_story(client, callback_query):
    user_id = callback_query.from_user.id

    
    cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
    ban_status = cursor.fetchone()[0]

    if ban_status == 'yes':
        await callback_query.message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        return

    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]
    
    if bot_setting == "off":
        await callback_query.message.reply("<b>ربات خاموش است</b>", quote=True)
        return
    
    if not await is_member(f"@{channel}", user_id):
        reply_markup = [
            [InlineKeyboardButton("🔐 | عضویت در کانال", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton('✅ | عضو شدم •', callback_data="Join")]
        ]
        await callback_query.message.reply('کاربر گرامی، برای استفاده از ربات ابتدا در کانال زیر عضو شوید 👇', reply_markup=InlineKeyboardMarkup(reply_markup), quote=True)
    else:
        callback_data = callback_query.data
        username = callback_data.replace("pagestory|", "")
    
        message = await callback_query.message.reply('<b>🔍 در حال دریافت اطلاعات استوری...</b>', quote=True)

        api = f"{web_url}?key={api_key}&type=pagestory&username={username}"
        response = requests.get(api)
        data = response.json()

        if data['status'] == 452:
            await message.edit_text('<b>♻️ پیج مورد نظر استوری ندارد</b>')
            return
        if data['status'] == 451:
            await message.edit_text('<b>🔒 پیج مورد نظر شخصی است</b>')
            return

        Number = len(data['result'])
        await message.edit_text(f"<b>🔱 لطفا صبر کنید\n🗂 تعداد عکس و فیلم ها: {Number}</b>")

        for i in range(Number):
            II = i + 1
            story = data['result'][i]['story']
            story_type = data['result'][i]['type']
            caption = f"<b>({II}/{Number})\n🤖 ارسال شده توسط : @{id_bot}</b>"
            if story_type == 'photo':
                await callback_query.message.reply_photo(story, caption=caption, quote=True)
            elif story_type == 'video':
                response = requests.head(story)
                video_size = int(response.headers.get('content-length', 0))
                if video_size < 20970000:
                    await callback_query.message.reply_video(story, caption=caption, quote=True)
                else:
                    response = requests.get(story)
                    rand = random.randint(1000, 9999999)
                    file_name = f"video-{rand}.mp4"
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    await callback_query.message.reply_video(file_name, caption=caption, quote=True)
                    os.remove(file_name)



@bot.on_callback_query(filters.regex(r'^pagehightlight\|'))
async def handle_highlight_callback(client, callback_query):
    user_id = callback_query.from_user.id

    
    cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
    ban_status = cursor.fetchone()[0]

    if ban_status == 'yes':
        await callback_query.message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        return

    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]
    
    if bot_setting == "off":
        await callback_query.message.reply("<b>ربات خاموش است</b>", quote=True)
        return
    
    if not await is_member(f"@{channel}", user_id):
        reply_markup = [
            [InlineKeyboardButton("🔐 | عضویت در کانال", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton('✅ | عضو شدم •', callback_data="Join")]
        ]
        await callback_query.message.reply('کاربر گرامی، برای استفاده از ربات ابتدا در کانال زیر عضو شوید 👇', reply_markup=InlineKeyboardMarkup(reply_markup), quote=True)
    else:
        data = callback_query.data.split('|')
        username = data[1]

        info_url = f"{web_url}?key={api_key}&type=pagehightlight&username={username}"
        sent_message = await callback_query.message.reply_text("<b>🔍 در حال دریافت اطلاعات هایلایت...</b>", quote=True)

        response = requests.get(info_url)
        data = response.json()

        if data['status'] == 453:
            await sent_message.edit_text("<b>♻️ پیج مورد نظر هایلایت ندارد</b>")
            return

        if data['status'] == 451:
            await sent_message.edit_text("<b>🔒 پیج مورد نظر شخصی است</b>")
            return

        keyboard_buttons = []

        for item in data["result"]:
            title = item["Title"]
            hightlightIDS = item["hightlightIDS"]
            button = InlineKeyboardButton(text=title, callback_data=f"highlight|{hightlightIDS}")
            keyboard_buttons.append([button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await callback_query.message.reply_text(f"<b>♻️ هایلایت های {username}</b>", reply_markup=keyboard, quote=True)


@bot.on_callback_query(filters.regex(r"highlight\|"))
async def page_story(client, callback_query):
    user_id = callback_query.from_user.id

    cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
    ban_status = cursor.fetchone()[0]

    if ban_status == 'yes':
        await callback_query.message.reply("<b>شما از ربات بن شده اید.</b>", quote=True)
        return

    cursor.execute("SELECT bot FROM settings WHERE id = 1")
    bot_setting = cursor.fetchone()[0]
    
    if bot_setting == "off":
        await callback_query.message.reply("<b>ربات خاموش است</b>", quote=True)
        return
    
    if not await is_member(f"@{channel}", user_id):
        reply_markup = [
            [InlineKeyboardButton("🔐 | عضویت در کانال", url=f"https://t.me/{channel}")],
            [InlineKeyboardButton('✅ | عضو شدم •', callback_data="Join")]
        ]
        await callback_query.message.reply('کاربر گرامی، برای استفاده از ربات ابتدا در کانال زیر عضو شوید 👇', reply_markup=InlineKeyboardMarkup(reply_markup), quote=True)
    else:
        callback_data = callback_query.data
        id = callback_data.replace("highlight|", "")

        sent_message = await callback_query.message.reply_text("<b>🔍 در حال دریافت هایلایت ها...</b>", quote=True)

        api = f"{web_url}?key={api_key}&type=gethightlight&id={id}"
        response = requests.get(api)
        data = response.json()

        Number = len(data['result'])
        await sent_message.edit_text(f"<b>🔱 لطفا صبر کنید\n🗂 تعداد عکس و فیلم ها: {Number}</b>")

        for i in range(Number):
            II = i + 1
            highlite = data['result'][i]['highlite']
            highlite_type = data['result'][i]['type']
            caption = f"<b>({II}/{Number})\n🤖 ارسال شده توسط : @{id_bot}</b>"
            if highlite_type == 'photo':
                await callback_query.message.reply_photo(highlite, caption=caption, quote=True)
            elif highlite_type == 'video':
                response = requests.head(highlite)
                video_size = int(response.headers.get('content-length', 0))
                if video_size < 20970000:
                    await callback_query.message.reply_video(highlite, caption=caption, quote=True)
                else:
                    response = requests.get(highlite)
                    rand = random.randint(1000, 9999999)
                    file_name = f"video-{rand}.mp4"
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    await callback_query.message.reply_video(file_name, caption=caption, quote=True)
                    os.remove(file_name)


panel_keyboard = [
    ["📈 | آمار •", "💤 | خاموش/روشن •"],
    ["📨 | پیام به کاربر •", "📥 | ارسال همگانی •"],
    ["🚫 | مسدود / آزاد •"],
    ["🏛"]
]
back_keyboard = [
    ["🔙 | برگشت •"]
]

@bot.on_message(filters.command("panel") & filters.private & filters.chat(admins))
async def admin_panel_command(client, message):
    markup = ReplyKeyboardMarkup(panel_keyboard, resize_keyboard=True)
    await message.reply_text("<b>◾️ ادمین گرامی ، به پنل مدیریتی خوش آمدید.</b>", reply_markup=markup, quote=True)

@bot.on_message(filters.private & filters.chat(admins))
async def admin_panel(client, message):
    text = message.text
    user_id = message.from_user.id
    cursor.execute("SELECT step FROM users WHERE user_id = %s", (user_id,))
    step = cursor.fetchone()[0]
    
    if message.text == "🔙 | برگشت •":
        cursor.execute("UPDATE users SET step = 'none' WHERE user_id = %s", (user_id,))
        db.commit()
        markup = ReplyKeyboardMarkup(panel_keyboard, resize_keyboard=True)
        await message.reply_text("به پنل مدیریت برگشتیم ... ", reply_markup=markup, quote=True)
        
    elif message.text == "🏛":
        await message.reply_text("به منوی اصلی برگشتید", reply_markup=ReplyKeyboardRemove(), quote=True)
       
    elif text == "📈 | آمار •":
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT bot FROM settings WHERE id = 1")
        bot_setting = cursor.fetchone()[0]

        if bot_setting == "on":
            bot_status = "روشن"
        else:
            bot_status = "خاموش"

        await message.reply_text(f"» آمار کل ربات : {user_count} نفر\n» وضعیت ربات : {bot_status}", quote=True)

    elif text == "💤 | خاموش/روشن •":
        cursor.execute("SELECT bot FROM settings WHERE id = 1")
        bot_setting = cursor.fetchone()[0]

        if bot_setting == "on":
            update_query = "UPDATE settings SET bot = 'off' WHERE id = 1"
            action_message = "ربات خاموش شد"
        else:
            update_query = "UPDATE settings SET bot = 'on' WHERE id = 1"
            action_message = "ربات روشن شد"

        cursor.execute(update_query)
        db.commit()

        await message.reply_text(action_message, quote=True)

    elif message.text == "📨 | پیام به کاربر •":
        cursor.execute("UPDATE users SET step = 'send-message' WHERE user_id = %s", (user_id,))
        db.commit()
        markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
        await message.reply_text("پیام خود را به صورت زیر ارسال کنید 👇\n[آیدی کاربر]\n[متن پیام]", reply_markup=markup, quote=True)

    elif step == "send-message":
        markup = ReplyKeyboardMarkup(panel_keyboard, resize_keyboard=True)
        cursor.execute("UPDATE users SET step = 'none' WHERE user_id = %s", (user_id,))
        db.commit()
        text_parts = message.text.split("\n")
        if len(text_parts) == 2:
            id = text_parts[0]
            text = text_parts[1]
            if id.isdigit():
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (id,))
                result = cursor.fetchone()
                if result is None:
                    await message.reply_text("⚠️ کاربر عضو ربات نمی‌باشد", reply_markup=markup, quote=True)
                else:
                    await bot.send_message(id, f"👨‍💻 یک پیام از طرف مدیریت\n\n{text}")
                    await message.reply_text("پیام شما با موفقیت ارسال شد", reply_markup=markup, quote=True)
            else:
                await message.reply_text("⚠️ آیدی کاربر باید یک عدد باشد", reply_markup=markup, quote=True)
        else:
            await message.reply_text("⚠️ ورودی نامعتبر. لطفاً آیدی کاربر و متن پیام را با دستور جداگانه وارد کنید.", reply_markup=markup, quote=True)

    elif message.text == "📥 | ارسال همگانی •":
        cursor.execute("UPDATE users SET step = 'send-all' WHERE user_id = %s", (user_id,))
        db.commit()
        markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
        await message.reply_text("متن پیام خود را ارسال کنید 👇", reply_markup=markup, quote=True)
        
    elif step == "send-all":
        markup = ReplyKeyboardMarkup(panel_keyboard, resize_keyboard=True)
        cursor.execute("UPDATE users SET step = 'none' WHERE user_id = %s", (user_id,))
        db.commit()
        await message.reply_text("در حال ارسال... ، لطفا تا اتمام فرایند به ربات دستوری ارسال نکنید ❗️", reply_markup=markup)

        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        for user in users:
            user_id = user[0]
            await bot.send_message(user_id, message.text)
        await message.reply_text("فرایند ارسال همگانی به اتمام رسید ✅", reply_markup=markup)

    elif message.text == "🚫 | مسدود / آزاد •":
        cursor.execute("UPDATE users SET step = 'ban-unban' WHERE user_id = %s", (user_id,))
        db.commit()
        markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
        await message.reply_text("آیدی عددی کاربر را ارسال کنید.", reply_markup=markup, quote=True)

    elif step == "ban-unban":
        markup = ReplyKeyboardMarkup(panel_keyboard, resize_keyboard=True)
        cursor.execute("UPDATE users SET step = 'none' WHERE user_id = %s", (user_id,))
        db.commit()
        id = message.text
        if id.isdigit():
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (id,))
            result = cursor.fetchone()
        
            if result is None:
                await message.reply_text("⚠️ کاربر عضو ربات نمی‌باشد", reply_markup=markup, quote=True)
            else:
                cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
                users_status = cursor.fetchone()[0]
                
                if users_status == "yes":
                    cursor.execute("UPDATE users SET ban = 'no' WHERE user_id = %s", (id,))
                    db.commit()
                    action_message = "کاربر رفع مسدود شد"
                else:
                    cursor.execute("UPDATE users SET ban = 'yes' WHERE user_id = %s", (id,))
                    db.commit()
                    action_message = "کاربر مسدود شد"
                await message.reply_text(action_message, reply_markup=markup,quote=True)
        else:
            await message.reply_text("⚠️ آیدی کاربر باید یک عدد باشد", reply_markup=markup, quote=True)

bot.run()