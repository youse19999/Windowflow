import sims4.commands
import subprocess
import server_commands.sim_commands
import services
import world.travel_service
from typing import Any
from protocolbuffers import Consts_pb2
from sims4communitylib.classes.interactions.common_terrain_interaction import CommonTerrainInteraction
from sims.sim import Sim
from event_testing.results import TestResult
from interactions.context import InteractionContext

from sims.sim_info_lod import SimInfoLODLevel
from objects.components import types
import build_buy

#脱獄用
import services
from event_testing.tests import TunableTestSet
from interactions.interaction_finisher import FinishingType
from interactions import ParticipantType
from objects import HiddenReasonFlag, ALL_HIDDEN_REASONS
from sims.daycare import DaycareLiability
import placement
import interactions.rabbit_hole
import interactions.utils.death_interactions

#インポートしてねぇ
from pprint import pformat
from sims4.tuning.tunable import HasTunableReference, TunableList, TunableTuple, TunableEnumEntry, TunableRange, TunableEnumWithFilter, Tunable, TunablePercent
from ui.ui_dialog_notification import UiDialogNotification
from sims4communitylib.notifications.common_basic_notification import CommonBasicNotification
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
from filters.sim_template import SimTemplateType, TunableSimTemplate
import filters.household_template
import tag
import relationships.relationship_bit
from sims.genealogy_tracker import FamilyRelationshipIndex
HOUSEHOLD_FILTER_PREFIX = ['household_member']
logger = sims4.log.Logger('Death Interactions')
aINSTANCE_TUNABLES = {'_household_members': filters.household_template._get_tunable_household_member_list(template_type=SimTemplateType.HOUSEHOLD, is_optional=True), '_household_funds': TunableRange(description='\n            Starting funds for this household.\n            ', tunable_type=int, default=99999999, minimum=0, maximum=9), '_household_relationship': TunableList(description='\n            Matrix of relationship that should be applied to household members.\n            ', tunable=TunableTuple(x=TunableEnumWithFilter(description='\n                    Tag of the household member to apply relationship to.\n                    ', tunable_type=tag.Tag, default=tag.Tag.INVALID, filter_prefixes=HOUSEHOLD_FILTER_PREFIX), y=TunableEnumWithFilter(description='\n                    Tag of the household member to be the target of relationship.\n                    ', tunable_type=tag.Tag, default=tag.Tag.INVALID, filter_prefixes=HOUSEHOLD_FILTER_PREFIX), is_spouse=Tunable(description='\n                    Check if x and y are spouses.\n                    ', tunable_type=bool, default=False), is_parentless_sibling=Tunable(description='\n                    Sibling relationship is automatically identified if x and y\n                    share a parent. If there is no parent in this household,\n                    checking this will establish their sibling relationship.\n                    \n                    At the moment, no additional family relationships are\n                    supported on these Sims. For example, these Sims cannot\n                    have an actual parent nor any children/grandchildren. If\n                    you require this functionality, please talk to a GPE.\n                    ', tunable_type=bool, default=False), family_relationship=TunableEnumEntry(description='\n                    This is the family relationship between x and y.\n                    Example: if set to Father, x is the the father of y.\n                    ', tunable_type=FamilyRelationshipIndex, default=None), relationship_bits=TunableList(description='\n                    Relationship bits that should be applied to x with\n                    the target y. Any bits with a relationship track will add\n                    relationship track at value that will add the bit to both\n                    sims.  Any bits without Triggered track will only be\n                    applied only to x unless it is a Siginificant other Bit.\n                    \n                    Example: If friendship-friend bit is supplied which has a\n                    triggered track of LTR_Friendship_Main, then\n                    LTR_Frienship_main will be added to both sims with a random\n                    value of the min/max value of the bit data tuning that will\n                    supply bit.\n                    ', tunable=relationships.relationship_bit.RelationshipBit.TunableReference())))}
#manymanymany32
@sims4.commands.Command('jailbreak', command_type=sims4.commands.CommandType.Live)
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
            output("Jailbreaking...")
            interactions.rabbit_hole.HideSimLiability.on_run = on_run
            nof("脱獄ツール","ラビットホールのが")
            interactions.utils.death_interactions.DeathSuperInteraction._finalize_death = _finalize_death
            nof("脱獄ツール","死のが")
            filters.household_template.HouseholdTemplate.INSTANCE_TUNABLES = aINSTANCE_TUNABLES
            nof("脱獄ツール","完了したよ")
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
                name=CommonLocalizationUtils.create_localized_string("脱獄を実行する"),
                #概要
                row_description=CommonLocalizationUtils.create_localized_string("ツールだよ！"),
                #ホールドででるやつ
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 1'
            ),
        ]
        dialog = CommonChooseObjectDialog(
            "脱獄ツール",
            "現在脱獄を行っています。待っていてください。ハッキングが終了するまで待っていてください。",
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

@sims4.commands.Command('afterdeathmenu', command_type=sims4.commands.CommandType.Live)
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
            output("Jailbreaking...")
            interactions.rabbit_hole.HideSimLiability.on_run = on_run
            nof("脱獄ツール","ラビットホールのが")
            interactions.death_interactions.DeathElement._finalize_death = _finalize_death
            nof("脱獄ツール","死のが")
            nof("脱獄ツール","完了したよ")
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
                name=CommonLocalizationUtils.create_localized_string("シムを完全に殺す"),
                #概要
                row_description=CommonLocalizationUtils.create_localized_string("ツールだよ！"),
                #ホールドででるやつ
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 1'
            ),
            ObjectPickerRow(
                #オプションの順位？
                option_id=2,
                #名前
                name=CommonLocalizationUtils.create_localized_string("選択を出さない"),
                #概要
                row_description=CommonLocalizationUtils.create_localized_string("ツールだよ！"),
                #ホールドででるやつ
                row_tooltip=None,
                icon=CommonIconUtils._load_icon(0x0000012331231212),
                tag='Value 1'
            ),
        ]
        dialog = CommonChooseObjectDialog(
            "死後のメニュー",
            "ダイアログを表示しますか？",
            tuple(options),
            title_tokens=title_tokens,
            description_tokens=description_tokens,
            per_page=1
        )
        dialog.show(on_chosen=_on_chosen)
    except Exception as ex:
        CommonExceptionHandler.log_exception(ModInfo.get_identity(), 'Failed to show dialog', exception=ex)
        output('Failed to show dialog, please locate your exception log file.')
    output('Done showing.')
    output("[+]Made by monaca")

def on_run(self):
        nof("Alert","シムがラビットホールを使用しました")
        for sim_info in self._sim_infos:
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return
            sims_to_hide = self.get_sims(sim)
            for sim in sims_to_hide:
                sim.fade_out()
                sim.hide(HiddenReasonFlag.RABBIT_HOLE)
                sim.client.selectable_sims.notify_dirty()
            valid_sims = (self._interaction.sim, self._interaction.target) + sims_to_hide
            for interaction in tuple(sim.interaction_refs):
                if interaction not in sim.interaction_refs:
                    pass
                elif interaction.sim in valid_sims:
                    pass
                else:
                    interaction.cancel(FinishingType.OBJECT_CHANGED, cancel_reason_msg='Target Sim was hidden by the HideSimLiability')
            for sim in sims_to_hide:
                sim.remove_location_from_quadtree(placement.ItemType.SIM_POSITION)
                sim.remove_location_from_quadtree(placement.ItemType.SIM_INTENDED_POSITION)
            for routing_slave in self._interaction.get_participants(ParticipantType.RoutingSlaves):
                for (state_value, tests) in self.ROUTING_SLAVE_ENTRY_STATE.items():
                    if state_value is not None and tests.run_tests(resolver=self._interaction.get_resolver()):
                        routing_slave.set_state(state_value.state, state_value)
                        break
                routing_slave.fade_out()
                routing_slave.hide(HiddenReasonFlag.RABBIT_HOLE)
                routing_slave.remove_location_from_quadtree(placement.ItemType.SIM_POSITION)
                routing_slave.remove_location_from_quadtree(placement.ItemType.SIM_INTENDED_POSITION)
            self._has_hidden = True
def _show_death_dialog(self):
        if self._client is not None:
            #dialog = self.death_dialog(self.sim, text=lambda *args, **kwargs: self.death_dialog.text(*args, household=self._client.household, **kwargs), resolver=SingleSimResolver(self.sim))
            #dialog.show_dialog()
            a = 0
def _finalize_death(self):
        nof("死にました","どんまい")
        if self._has_finalized_death:
            return
        self._has_finalized_death = True
        sim_info = self.sim.sim_info
        current_household = sim_info.household
        death_object = self._death_object_data[0]
        if death_object is not None:
            death_object.add_dynamic_component(types.STORED_SIM_INFO_COMPONENT, sim_id=sim_info.id)
            death_object.update_object_tooltip()
            active_household = services.active_household()
            death_object.set_household_owner_id(active_household.id)
            if self._death_object_data[1]:
                try:
                    if not build_buy.move_object_to_household_inventory(death_object):
                        logger.error('Failed to place an urnstone for {} in household inventory: {}', sim_info, sim_info.household.id)
                except KeyError:
                    logger.exception('Failed to place an urnstone for {} in household inventory: {}', sim_info, sim_info.household.id)
        death_tracker = sim_info.death_tracker
        death_type = None
        if self.death_info is not None:
            death_type = self.death_info.death_type
        death_tracker.set_death_type(death_type)
        if self._should_set_to_min_lod():
            sim_info.request_lod(SimInfoLODLevel.MINIMUM)
        if self._client is not None:
            self._client.set_next_sim_or_none(only_if_this_active_sim_info=sim_info)
            self._client.selectable_sims.remove_selectable_sim_info(sim_info)
            kill_all_fires = False
            if any(sim.can_live_alone for sim in self._client.selectable_sims):
                if self._show_off_lot_death_notification():
                    kill_all_fires = True
            else:
                kill_all_fires = True
                self._disband_travel_group()
                self._show_death_dialog()
                self._client.clear_selectable_sims()
            if kill_all_fires:
                fire_service = services.get_fire_service()
                if fire_service is not None:
                    fire_service.kill()
        current_household.handle_adultless_household()
        services.daycare_service().refresh_household_daycare_nanny_status(sim_info)
        
def nof(title,dis):
    try:
        # LocalizedStrings within other LocalizedStrings
        title_tokens = (
            CommonLocalizationUtils.create_localized_string(
                "title",
                text_color=CommonLocalizedStringColor.BLUE
            ),
        )
        description_tokens = (
            CommonLocalizationUtils.create_localized_string(
                "dis",
                text_color=CommonLocalizedStringColor.BLUE
            ),
        )
        dialog = CommonBasicNotification(
            title,
            dis,
            title_tokens=title_tokens,
            description_tokens=description_tokens,
            urgency=UiDialogNotification.UiDialogNotificationUrgency.DEFAULT
        )
        dialog.show()
    except Exception as ex:
        CommonExceptionHandler.log_exception(ModInfo.get_identity(), 'Failed to show a basic notification', exception=ex)
