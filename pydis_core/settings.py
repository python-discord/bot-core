from pydantic import BaseSettings


class EnvConfig(BaseSettings):
    """Our default configuration for models that should load from .env files."""

    class Config:
        """Specify what .env files to load, and how to load them."""

        env_file = ".env.server", ".env",
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


class _Channels(EnvConfig):
    EnvConfig.Config.env_prefix = "channels_"

    announcements = 354619224620138496
    changelog = 748238795236704388
    mailing_lists = 704372456592506880
    python_events = 729674110270963822
    python_news = 704372456592506880
    reddit = 458224812528238616

    dev_contrib = 635950537262759947
    dev_core = 411200599653351425
    dev_log = 622895325144940554

    meta = 429409067623251969
    python_general = 267624335836053506

    python_help = 1035199133436354600

    attachment_log = 649243850006855680
    filter_log = 1014943924185473094
    message_log = 467752170159079424
    mod_log = 282638479504965634
    nomination_voting_archive = 833371042046148738
    user_log = 528976905546760203
    voice_log = 640292421988646961

    off_topic_0 = 291284109232308226
    off_topic_1 = 463035241142026251
    off_topic_2 = 463035268514185226

    bot_commands = 267659945086812160
    discord_bots = 343944376055103488
    esoteric = 470884583684964352
    voice_gate = 764802555427029012
    code_jam_planning = 490217981872177157

    # Staff
    admins = 365960823622991872
    admin_spam = 563594791770914816
    defcon = 464469101889454091
    helpers = 385474242440986624
    incidents = 714214212200562749
    incidents_archive = 720668923636351037
    mod_alerts = 473092532147060736
    mod_meta = 775412552795947058
    mods = 305126844661760000
    nominations = 822920136150745168
    nomination_discussion = 798959130634747914
    nomination_voting = 822853512709931008
    organisation = 551789653284356126

    # Staff announcement channels
    admin_announcements = 749736155569848370
    mod_announcements = 372115205867700225
    staff_announcements = 464033278631084042
    staff_info = 396684402404622347
    staff_lounge = 464905259261755392

    # Voice Channels
    admins_voice = 500734494840717332
    code_help_voice_0 = 751592231726481530
    code_help_voice_1 = 764232549840846858
    general_voice_0 = 751591688538947646
    general_voice_1 = 799641437645701151
    staff_voice = 412375055910043655

    black_formatter = 846434317021741086

    # Voice Chat
    code_help_chat_0 = 755154969761677312
    code_help_chat_1 = 766330079135268884
    staff_voice_chat = 541638762007101470
    voice_chat_0 = 412357430186344448
    voice_chat_1 = 799647045886541885

    big_brother = 468507907357409333
    duck_pond = 637820308341915648
    roles = 851270062434156586

    rules = 693837295685730335
