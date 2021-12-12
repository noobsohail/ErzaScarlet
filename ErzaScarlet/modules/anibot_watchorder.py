from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from ErzaScarlet import BOT_USERNAME as  BOT_NAME, TRIGGERS as trg, pbot as anibot
from ErzaScarlet.helper_extra.anibot.data_parser import get_wo, get_wols
from ErzaScarlet.helper_extra.anibot.helper import check_user, control_user
from ErzaScarlet.helper_extra.anibot.db import get_collection

DC = get_collection('DISABLED_CMDS')


@anibot.on_message(filters.command(["watchorder", f"watchorder{BOT_NAME}"], prefixes=trg))
@control_user
async def get_watch_order(client: anibot, message: Message, mdata: dict):
    """Get List of Scheduled Anime"""
    gid = mdata['chat']['id']
    find_gc = await DC.find_one({'_id': gid})
    if find_gc is not None and 'watch' in find_gc['cmd_list'].split():
        return
    x = message.text.split(" ", 1)
    if len(x)==1:
        await message.reply_text("Nothing given to search for!!!")
        return
    user = mdata['from_user']['id']
    data = get_wols(x[1])
    msg = f"Found related animes for the query {x[1]}"
    buttons = []
    if data == []:
        await client.send_message(gid, 'No results found!!!')
        return
    for i in data:
        buttons.append([InlineKeyboardButton(str(i[1]), callback_data=f"watch_{i[0]}_{x[1]}_0_{user}")])
    await client.send_message(gid, msg, reply_markup=InlineKeyboardMarkup(buttons))


@anibot.on_callback_query(filters.regex(pattern=r"watch_(.*)"))
@check_user
async def watch_(client: anibot, cq: CallbackQuery, cdata: dict):
    kek, id_, qry, req, user = cdata['data'].split("_")
    msg, total = get_wo(int(id_), int(req))
    totalpg, lol = divmod(total, 50)
    button = []
    if lol!=0:
        totalpg + 1
    if total>50:
        if int(req)==0:
            button.append([InlineKeyboardButton(text="Next", callback_data=f"{kek}_{id_}_{qry}_{int(req)+1}_{user}")])
        elif int(req)==totalpg:
            button.append([InlineKeyboardButton(text="Prev", callback_data=f"{kek}_{id_}_{qry}_{int(req)-1}_{user}")])
        else:
            button.append(
                [
                    InlineKeyboardButton(text="Prev", callback_data=f"{kek}_{id_}_{qry}_{int(req)-1}_{user}"),
                    InlineKeyboardButton(text="Next", callback_data=f"{kek}_{id_}_{qry}_{int(req)+1}_{user}")
                ]
            )
    button.append([InlineKeyboardButton("Back", callback_data=f"wol_{qry}_{user}")])
    await cq.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(button))


@anibot.on_callback_query(filters.regex(pattern=r"wol_(.*)"))
@check_user
async def wls(client: anibot, cq: CallbackQuery, cdata: dict):
    kek, qry, user = cdata['data'].split("_")
    data = get_wols(qry)
    msg = f"Found related animes for the query {qry}"
    buttons = []
    for i in data:
        buttons.append([InlineKeyboardButton(str(i[1]), callback_data=f"watch_{i[0]}_{qry}_0_{user}")])
    await cq.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))