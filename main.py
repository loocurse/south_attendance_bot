# Jon you can use these functions for conversations
from backend import *

import logging

from time import sleep
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode, Poll
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    PollAnswerHandler,
    ConversationHandler,
    CallbackContext,
    PollHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CG, NAMES, POLLANSWER = range(3)

def start(update,context) -> int:
    reply_keyboard = [['SA A', 'CJ A'],
                      ['SA B', 'CJ B'],
                      ['SA C', 'CJ C'],
                      ]

    update.message.reply_text(
        'Hi! I am a loyal servant to South, I will be helping you with your CG attendance. '
        'Send /cancel to stop talking to me.\n\n'
        'Which CG are you taking attendance for?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return CG

def cg(update,context) -> int:
    CG = update.message.text
    context.user_data['CG'] = CG
    user = update.message.from_user
    logger.info("CG of %s: %s (message_id: %s)", user.first_name, update.message.text, user.id)
    update.message.reply_text(
        'You have picked {} CG,\n '
        'Click /cancel to stop . \n or /NAMES to continue'.format(context.user_data['CG']),
        reply_markup=ReplyKeyboardRemove(),
    )



    return NAMES


def poll(update,context) -> None:
    """Sends a predefined poll"""
    questions = get_youths(context.user_data['CG']) #['jon', 'lucas', 'vans', 'rox', 'nay', 'rach']
    print(questions)
    if len(questions) > 10:
        questions2 = questions[10:]
        questions = questions[:9]
        message = context.bot.send_poll(
            update.effective_chat.id,
            "Which youths came?",
            questions,
            is_anonymous=False,
            allows_multiple_answers=True,
        )
        # Save some info about the poll the bot_data for later use in receive_poll_answer
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)
        message = context.bot.send_poll(
            update.effective_chat.id,
            "Which youths came?",
            questions2,
            is_anonymous=False,
            allows_multiple_answers=True,
        )
        # Save some info about the poll the bot_data for later use in receive_poll_answer
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)

        #----- else:  (when CG youths <=10)
    else:
        message = context.bot.send_poll(
            update.effective_chat.id,
            "Which youths came?",
            questions,
            is_anonymous=False,
            allows_multiple_answers=True,
        )
        # Save some info about the poll the bot_data for later use in receive_poll_answer
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)

    return POLLANSWER

def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    attendance = []
    for question_id in selected_options:
        attendance.append(questions[question_id])
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} took attendance for {context.user_data['CG']} youths!  {attendance}\n \nThank you for using me! See you again soon!! \nGoodbye",
        parse_mode=ParseMode.HTML,
    )

    logger.info("%s names keyed in", context.user_data['CG'])
    # Close poll

    context.bot.stop_poll(
        context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
    )
    context.user_data['ATTENDANCE'] = attendance

    return ConversationHandler.END
    #return END

# def end(update,context):
#     update.message.reply_text('{} Sheep successfully accounted for!.'.format(context.user_data['CG']))
#     return ConversationHandler.END

def error(update,context):
    logger.warning('Update "%s" caused error "%s"',update,context.error)

def cancel(update,context) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1072816356:AAFxN3QCAnlFxodH_yuaUEn0aix_5DPHzIw", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CG, NAMES

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CG: [CommandHandler('cancel', cancel),
                           MessageHandler(Filters.all,
                                          cg),
                           ],
            NAMES: [CommandHandler('cancel', cancel),
                           CommandHandler('NAMES', poll),
                    PollHandler(poll)],
            POLLANSWER: [CommandHandler('cancel', cancel),
                        PollAnswerHandler(receive_poll_answer),
                        ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_chat=False,
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    #dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    #dispatcher.add_handler(PollHandler(poll))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
