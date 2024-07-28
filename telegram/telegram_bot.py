import logging
import sys

from decouple import config
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

from constants import LOCATION, EXPERIENCE, SALARY

TELEGRAM_API_KEY = config("TELEGRAM_API_KEY", None)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramAnswersDTO:
    def __init__(self, site, location, experience, salary):
        self.site = site
        self.location = location
        self.experience = experience
        self.salary = salary
        self.skills = None


class TelegramBot:
    def __init__(self):
        self.API_KEY = TELEGRAM_API_KEY
        # self.DEFAULT_BOT_URL = "https://api.telegram.org/bot" + self.API_KEY
        self.CHOOSING_OPTION = 0
        self.ASKING_LOCATION = 1
        self.ASKING_EXPERIENCE = 2
        self.ASKING_SALARY = 3
        self.CONFIRMING = 4

        self.reply_keyboard = [
            ["work.ua", "rabota.ua"],
            ["exit"],
        ]

        self.answers = TelegramAnswersDTO(None, None, None, None)
        self.validate_api_key_not_empty()

    def validate_api_key_not_empty(self) -> None:
        if not self.API_KEY:
            logger.error(
                "API key not found. "
                "Please set the valid TELEGRAM_API_KEY environment variable."
                "Closing the application..."
            )
            sys.exit(1)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Hi! I'm the *Bot for candidates scraping*.\n"
            "Please choose a site to scrape.",
            parse_mode="markdown",
            disable_web_page_preview=True,
            reply_markup=ReplyKeyboardMarkup(self.reply_keyboard),
        )
        return self.CHOOSING_OPTION

    async def handle_user_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_choice = update.message.text.lower()

        if user_choice in ["work.ua", "rabota.ua"]:
            self.answers.site = user_choice
            await update.message.reply_text("You chose {}.\nPlease select a location:".format(user_choice))
            return await self.ask_location(update, context)

        elif user_choice == "exit":
            await update.message.reply_text("Bye!", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        else:
            await update.message.reply_text("Invalid choice. Please select a valid option.")
            return self.CHOOSING_OPTION

    async def ask_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [
            [InlineKeyboardButton(loc, callback_data=loc) for loc in list(LOCATION.keys())[i:i + 2]]
            for i in range(0, len(LOCATION.keys()), 2)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose a location:", reply_markup=reply_markup)
        return self.ASKING_LOCATION

    async def location_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        self.answers.location = query.data
        await query.edit_message_text(text=f"Selected location: {query.data}\nPlease select the experience required:")
        return await self.ask_experience(update, context)

    async def ask_experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [
            [InlineKeyboardButton(exp, callback_data=exp) for exp in list(EXPERIENCE.keys())[i:i + 2]]
            for i in range(0, len(EXPERIENCE.keys()), 2)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose experience:", reply_markup=reply_markup)
        return self.ASKING_EXPERIENCE

    async def experience_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        self.answers.experience = query.data
        await query.edit_message_text(text=f"Selected experience: {query.data}\nPlease select the salary range:")
        return await self.ask_salary(update, context)

    async def ask_salary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [
            [InlineKeyboardButton(salary, callback_data=salary) for salary in list(SALARY.keys())[i:i + 2]]
            for i in range(0, len(SALARY.keys()), 2)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose a salary range:", reply_markup=reply_markup)
        return self.ASKING_SALARY

    async def salary_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        self.answers.salary = query.data
        await query.edit_message_text(text=f"Selected salary: {query.data}\nPlease confirm the details:\nSite: {self.answers.site}\nLocation: {self.answers.location}\nExperience: {self.answers.experience}\nSalary: {self.answers.salary}\nType 'yes' to confirm or 'no' to abort.")
        return self.CONFIRMING

    async def confirm_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text.lower() == "yes":
            await update.message.reply_text("Starting the scraping process...")
            # Here you can call the method to start the spider and fetch results.
            results = self.run_spider(self.answers)
            await update.message.reply_text("Scraping completed. Here are the results:\n{}".format(results))
            return ConversationHandler.END
        else:
            await update.message.reply_text("Process aborted. Restart with /start")
            return ConversationHandler.END

    def run_spider(self, answers: TelegramAnswersDTO):
        return answers

    async def error_handler(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        logger.error("Exception occurred:", exc_info=context.error)

    async def exit(self, update: Update,
                   context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Conversation closed.")
        return ConversationHandler.END

    def main(self) -> None:
        logger.info("Running telegram bot...")
        application = Application.builder().token(self.API_KEY).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.CHOOSING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_user_choice)],
                self.ASKING_LOCATION: [CallbackQueryHandler(self.location_selected)],
                self.ASKING_EXPERIENCE: [CallbackQueryHandler(self.experience_selected)],
                self.ASKING_SALARY: [CallbackQueryHandler(self.salary_selected)],
                self.CONFIRMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm_details)],
            },
            fallbacks=[CommandHandler("exit", self.exit)],
        )

        application.add_handler(conv_handler)
        application.run_polling()


Telegram = TelegramBot()

if __name__ == "__main__":
    Telegram.main()
