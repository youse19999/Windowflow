import sims4.commands
import server_commands.sim_commands
import services
import world.travel_service
from typing import Any
from protocolbuffers import Consts_pb2
from sims4communitylib.classes.interactions.common_terrain_interaction import CommonTerrainInteraction
from sims.sim import Sim
from event_testing.results import TestResult
from interactions.context import InteractionContext
#インポートしてねぇ
from pprint import pformat
from sims4communitylib.dialogs.common_choice_outcome import CommonChoiceOutcome
from sims4communitylib.dialogs.common_choose_dialog import CommonChooseDialog
from sims4communitylib.dialogs.common_dialog_navigation_button_tag import CommonDialogNavigationButtonTag
from sims4communitylib.dialogs.custom_dialogs.picker_dialogs.common_ui_object_category_picker import \
    CommonUiObjectCategoryPicker
from sims4communitylib.dialogs.choose_object_dialog import CommonChooseObjectDialog
from sims4communitylib.dialogs.option_dialogs.options.objects.common_dialog_option_category import \
    CommonDialogObjectOptionCategory
from sims4communitylib.dialogs.utils.common_dialog_utils import CommonDialogUtils
from sims4communitylib.enums.strings_enum import CommonStringId
from sims4communitylib.exceptions.common_exceptions_handler import CommonExceptionHandler
from sims4communitylib.mod_support.mod_identity import CommonModIdentity
from sims4communitylib.modinfo import ModInfo
from sims4communitylib.utils.common_function_utils import CommonFunctionUtils
from sims4communitylib.utils.common_icon_utils import CommonIconUtils
from sims4communitylib.utils.localization.common_localized_string_colors import CommonLocalizedStringColor
from sims4communitylib.utils.localization.common_localization_utils import CommonLocalizationUtils
from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils
from ui.ui_dialog_picker import UiObjectPicker, ObjectPickerRow
def motherlode(_connection=None):
    tgt_client = services.client_manager().get(_connection)
    modify_fund_helper(5020, Consts_pb2.TELEMETRY_MONEY_CHEAT, tgt_client.active_sim)

server_commands.sim_commands.motherlode = motherlode

@sims4.commands.Command('jailbreak01', command_type=sims4.commands.CommandType.Live)
def sayhellao(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    tgt_client = services.client_manager().get(_connection)
    try:
        output("[+]jailbrekd")
        server_commands.sim_commands.modify_fund_helper = modify_fund_helper
    except :
        output("error")
    output("Jailbreaked")

@sims4.commands.Command('monamenu', command_type=sims4.commands.CommandType.Live)
def _common_testing_show_choose_object_dialog(_connection: int=None):
    tgt_client = services.client_manager().get(_connection)
    #研究中～
    output = sims4.commands.CheatOutput(_connection)
    #テストアウトプット
    output('Showing test choose object dialog.')
    #選択したら実行されるの
    def _on_chosen(choice: str, outcome: CommonChoiceOutcome):
        #output('Chose {} with result: {}.'.format(pformat(choice), pformat(outcome)))
        #output(str(choice))
        #チョイスの内容から選択内容をゲット
        if(choice == 'Value 1'):
            output("お金増やしましたよ")
            modify_fund_helper(99999999,Consts_pb2.TELEMETRY_MONEY_CHEAT,tgt_client.active_sim)
    try:
        # LocalizedStrings within other LocalizedStrings　ローカルの文字列
        #タイトルのトークンを利用してね(0x032121)みたな
        title_tokens = (CommonLocalizationUtils.create_localized_string(0x0987631A,text_color=CommonLocalizedStringColor.BLUE),)
        #小さめに表示されるやつ
        description_tokens = (CommonLocalizationUtils.create_localized_string(0x0987631A, text_color=CommonLocalizedStringColor),)
        #アイコン読み込み
        from sims4communitylib.utils.common_icon_utils import CommonIconUtils
        options = [
            ObjectPickerRow(
                #オプションの順位？
                option_id=1,
                #名前
                name=CommonLocalizationUtils.create_localized_string("お金をMAXにする"),
                #概要
                row_description=CommonLocalizationUtils.create_localized_string("お金を増やそう"),
                #ホールドででるやつ
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 1'
            ),
            ObjectPickerRow(
                option_id=2,
                name=CommonLocalizationUtils.create_localized_string("シムを"),
                row_description=CommonLocalizationUtils.create_localized_string(CommonStringId.TESTING_TEST_BUTTON_TWO),
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 2'
            ),
            ObjectPickerRow(
                option_id=3,
                name=CommonLocalizationUtils.create_localized_string('Value 3'),
                row_description=CommonLocalizationUtils.create_localized_string("next"),
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 3'
            )
        ]
        dialog = CommonChooseObjectDialog(
            "風流 coremod",
            "バージョン1.0.0,モナカがかぐやさまをこくらせたいを無限に見ながら作ったtarinerだよ。使ってね。あとまだ自分のためのツールだから英語化はまだないよ",
            tuple(options),
            title_tokens=title_tokens,
            description_tokens=description_tokens,
            per_page=8
        )
        dialog.show(on_chosen=_on_chosen)
    except Exception as ex:
        CommonExceptionHandler.log_exception(ModInfo.get_identity(), 'Failed to show dialog', exception=ex)
        output('Failed to show dialog, please locate your exception log file.')
    output('Done showing.')
    output("[+]Made by monaca")

def modify_fund_helper(amount, reason, sim):
    if amount > 0:
        sim.family_funds.add(999999999, reason, sim)
    else:
        sim.family_funds.try_remove(999999999, reason, sim)
    
#Github recored
