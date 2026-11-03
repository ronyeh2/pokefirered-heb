#include "global.h"
#include "link_rfu.h"
#include "mystery_gift_server.h"
#include "mystery_gift_client.h"
#include "constants/union_room.h"

ALIGNED(4) const u8 gText_UR_EmptyString[] = _("");
ALIGNED(4) const u8 gText_UR_Colon[] = _(":");
ALIGNED(4) const u8 gText_UR_ID[] = _("{ID}");
ALIGNED(4) const u8 gText_UR_PleaseStartOver[] = _("אנא התחל מחדש מההתחלה.");
ALIGNED(4) const u8 gText_UR_WirelessSearchCanceled[] = _("חיפוש מערכת התקשורת\nהאלחוטית בוטל.");
ALIGNED(4) static const u8 sText_AwaitingCommunucation2[] = _("ともだちからの れんらくを\nまっています");
ALIGNED(4) const u8 gText_UR_AwaitingCommunication[] = _("{STR_VAR_1}! ממתין לקשר\nמשחקן אחר.");
ALIGNED(4) const u8 gText_UR_AwaitingLinkPressStart[] = _("{STR_VAR_1}! ממתין לחיבור!\nלחץ TRATS כשכולם מוכנים.");

ALIGNED(4) static const u8 sText_SingleBattle[] = _("シングルバトルを かいさいする");
ALIGNED(4) static const u8 sText_DoubleBattle[] = _("ダブルバトルを かいさいする");
ALIGNED(4) static const u8 sText_MultiBattle[] = _("マルチバトルを かいさいする");
ALIGNED(4) static const u8 sText_TradePokemon[] = _("ポケモンこうかんを かいさいする");
ALIGNED(4) static const u8 sText_Chat[] = _("チャットを かいさいする");
ALIGNED(4) static const u8 sText_DistWonderCard[] = _("ふしぎなカードをくばる");
ALIGNED(4) static const u8 sText_DistWonderNews[] = _("ふしぎなニュースをくばる");
ALIGNED(4) static const u8 sText_DistMysteryEvent[] = _("ふしぎなできごとを かいさいする");
ALIGNED(4) static const u8 sText_HoldPokemonJump[] = _("なわとびを かいさいする");
ALIGNED(4) static const u8 sText_HoldBerryCrush[] = _("きのみマッシャーを かいさいする");
ALIGNED(4) static const u8 sText_HoldBerryPicking[] = _("きのみどりを かいさいする");
ALIGNED(4) static const u8 sText_HoldSpinTrade[] = _("ぐるぐるこうかんを かいさいする");
ALIGNED(4) static const u8 sText_HoldSpinShop[] = _("ぐるぐるショップを かいさいする");

// Unused
static const u8 *const sLinkGroupActionTexts[] = {
    sText_SingleBattle,
    sText_DoubleBattle,
    sText_MultiBattle,
    sText_TradePokemon,
    sText_Chat,
    sText_DistWonderCard,
    sText_DistWonderNews,
    sText_DistWonderCard,
    sText_HoldPokemonJump,
    sText_HoldBerryCrush,
    sText_HoldBerryPicking,
    sText_HoldBerryPicking,
    sText_HoldSpinTrade,
    sText_HoldSpinShop
};

static const u8 sText_1PlayerNeeded[] = _("דרוש\nשחקן אחד.");
static const u8 sText_2PlayersNeeded[] = _("דרושים\nשני שחקנים.");
static const u8 sText_3PlayersNeeded[] = _("דרושים\nשלושה שחקנים.");
static const u8 sText_4PlayersNeeded[] = _("あと4にん\nひつよう");
static const u8 sText_2PlayerMode[] = _("מצב\nשני שחקנים");
static const u8 sText_3PlayerMode[] = _("מצב\nשלושה שחקנים");
static const u8 sText_4PlayerMode[] = _("מצב\nארבעה שחקנים");
static const u8 sText_5PlayerMode[] = _("מצב\nחמישה שחקנים");

const u8 *const gTexts_UR_PlayersNeededOrMode[][5] = {
    { // 2 players required
        sText_1PlayerNeeded,
        sText_2PlayerMode
    },
    { // 4 players required
        sText_3PlayersNeeded,
        sText_2PlayersNeeded,
        sText_1PlayerNeeded,
        sText_4PlayerMode
    },
    { // 2-5 players required
        sText_1PlayerNeeded,
        sText_2PlayerMode,
        sText_3PlayerMode,
        sText_4PlayerMode,
        sText_5PlayerMode
    },
    { // 3-5 players required
        sText_2PlayersNeeded,
        sText_1PlayerNeeded,
        sText_3PlayerMode,
        sText_4PlayerMode,
        sText_5PlayerMode
    }
};

ALIGNED(4) const u8 gText_UR_BButtonCancel[] = _("{B_BUTTON}ביטול");
ALIGNED(4) static const u8 sText_SearchingForParticipants[] = _("ため\nさんかしゃ ぼしゅうちゅう です！");
ALIGNED(4) const u8 gText_UR_PlayerContactedYouForXAccept[] = _("{STR_VAR_2} יצר איתך קשר בשביל\n{STR_VAR_1}. לאשר?");
ALIGNED(4) const u8 gText_UR_PlayerContactedYouShareX[] = _("{STR_VAR_2} יצר איתך קשר.\nלשתף את {STR_VAR_1}?");
ALIGNED(4) const u8 gText_UR_PlayerContactedYouAddToMembers[] = _("{STR_VAR_2} יצר איתך קשר.\nלהוסיף לחברי הקבוצה?");
ALIGNED(4) const u8 gText_UR_AreTheseMembersOK[] = _("{STR_VAR_1}!\nהחברים האלה בסדר?");
ALIGNED(4) const u8 gText_UR_CancelModeWithTheseMembers[] = _("לבטל את מצב {STR_VAR_1}\nעם החברים האלה?");
ALIGNED(4) const u8 gText_UR_AnOKWasSentToPlayer[] = _("אישור נשלח\nאל {STR_VAR_1}.");

ALIGNED(4) static const u8 sText_OtherTrainerUnavailableNow[] = _("נראה שהמאמן השני אינו\nזמין כרגע…\p");
ALIGNED(4) static const u8 sText_CantTransmitTrainerTooFar[] = _("אי אפשר לשדר למאמן\nשנמצא רחוק מדי.\p");
ALIGNED(4) static const u8 sText_TrainersNotReadyYet[] = _("המאמנים האחרים עדיין\nלא מוכנים.\p");

const u8 *const gTexts_UR_CantTransmitToTrainer[] = {
    sText_CantTransmitTrainerTooFar,
    sText_TrainersNotReadyYet
};

ALIGNED(4) const u8 gText_UR_ModeWithTheseMembersWillBeCanceled[] = _("מצב {STR_VAR_1} עם החברים\nהאלה יבוטל.{PAUSE 90}");
ALIGNED(4) static const u8 sText_MemberNoLongerAvailable[] = _("יש חבר קבוצה שאינו יכול\nלהישאר זמין.\p");

const u8 *const gTexts_UR_PlayerUnavailable[] = {
    sText_OtherTrainerUnavailableNow,
    sText_MemberNoLongerAvailable
};

ALIGNED(4) static const u8 sText_TrainerAppearsUnavailable[] = _("נראה שהמאמן השני\nאינו זמין…\p");
ALIGNED(4) const u8 gText_UR_PlayerSentBackOK[] = _("{STR_VAR_1} החזיר אישור!");
ALIGNED(4) const u8 gText_UR_PlayerOKdRegistration[] = _("{STR_VAR_1} אישר את רישומך\nכחבר קבוצה.");
ALIGNED(4) static const u8 sText_PlayerRepliedNo[] = _("{STR_VAR_1} ענה, “לא…”\p");
ALIGNED(4) const u8 gText_UR_AwaitingOtherMembers[] = _("{STR_VAR_1}!\nממתין לחברים נוספים!");
ALIGNED(4) const u8 gText_UR_QuitBeingMember[] = _("להפסיק להיות חבר קבוצה?");
ALIGNED(4) static const u8 sText_StoppedBeingMember[] = _("הפסקת להיות חבר קבוצה.\p");

const u8 *const gTexts_UR_PlayerDisconnected[] = {
    [RFU_STATUS_OK]                  = NULL,
    [RFU_STATUS_FATAL_ERROR]         = sText_MemberNoLongerAvailable,
    [RFU_STATUS_CONNECTION_ERROR]    = sText_TrainerAppearsUnavailable,
    [RFU_STATUS_CHILD_SEND_COMPLETE] = NULL,
    [RFU_STATUS_NEW_CHILD_DETECTED]  = NULL,
    [RFU_STATUS_JOIN_GROUP_OK]       = NULL,
    [RFU_STATUS_JOIN_GROUP_NO]       = sText_PlayerRepliedNo,
    [RFU_STATUS_WAIT_ACK_JOIN_GROUP] = NULL,
    [RFU_STATUS_LEAVE_GROUP_NOTICE]  = NULL,
    [RFU_STATUS_LEAVE_GROUP]         = sText_StoppedBeingMember
};

ALIGNED(4) const u8 gText_UR_WirelessLinkEstablished[] = _("החיבור למערכת התקשורת\nהאלחוטית נוצר.");
ALIGNED(4) const u8 gText_UR_WirelessLinkDropped[] = _("החיבור למערכת התקשורת\nהאלחוטית נותק…");
ALIGNED(4) const u8 gText_UR_LinkWithFriendDropped[] = _("החיבור עם החבר שלך\nנותק…");
ALIGNED(4) static const u8 sText_PlayerRepliedNo2[] = _("{STR_VAR_1} ענה, “לא…”");

const u8 *const gTexts_UR_LinkDropped[] = {
    [RFU_STATUS_OK]                  = NULL,
    [RFU_STATUS_FATAL_ERROR]         = gText_UR_LinkWithFriendDropped,
    [RFU_STATUS_CONNECTION_ERROR]    = gText_UR_LinkWithFriendDropped,
    [RFU_STATUS_CHILD_SEND_COMPLETE] = NULL,
    [RFU_STATUS_NEW_CHILD_DETECTED]  = NULL,
    [RFU_STATUS_JOIN_GROUP_OK]       = NULL,
    [RFU_STATUS_JOIN_GROUP_NO]       = sText_PlayerRepliedNo2,
    [RFU_STATUS_WAIT_ACK_JOIN_GROUP] = NULL,
    [RFU_STATUS_LEAVE_GROUP_NOTICE]  = NULL,
    [RFU_STATUS_LEAVE_GROUP]         = NULL
};

ALIGNED(4) static const u8 sText_DoYouWantXMode[] = _("האם תרצה את מצב\n{STR_VAR_2}?");
ALIGNED(4) static const u8 sText_DoYouWantXMode2[] = _("האם תרצה את מצב\n{STR_VAR_2}?");

// Unused
static const u8 *const sDoYouWantModeTexts[] = {
    sText_DoYouWantXMode,
    sText_DoYouWantXMode2
};

ALIGNED(4) static const u8 sText_CommunicatingPleaseWait[] = _("はなしかけています…\nしょうしょう おまちください"); // Unused
ALIGNED(4) const u8 gText_UR_AwaitingPlayersResponseAboutTrade[] = _("ממתין לתשובת {STR_VAR_1}\nבנוגע להחלפה…");

ALIGNED(4) static const u8 sText_Communicating[] = _("מתקשר{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.\n{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.");
ALIGNED(4) static const u8 sText_CommunicatingWithPlayer[] = _("מתקשר עם {STR_VAR_1}{STR_VAR_1}{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.\n{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.");
ALIGNED(4) static const u8 sText_PleaseWaitAWhile[] = _("אנא המתן רגע{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.\n{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.{PAUSE 15}.");

const u8 *const gTexts_UR_CommunicatingWait[] = {
    sText_Communicating,
    sText_CommunicatingWithPlayer,
    sText_PleaseWaitAWhile
};

ALIGNED(4) static const u8 sText_HiDoSomethingMale[] = _("היי! יש משהו שרצית\nלעשות?");
ALIGNED(4) static const u8 sText_HiDoSomethingFemale[] = _("שלום!\nתרצה לעשות משהו?");
ALIGNED(4) static const u8 sText_HiDoSomethingAgainMale[] = _("{STR_VAR_1}: היי, נפגשנו שוב!\nמה בא לך הפעם?");
ALIGNED(4) static const u8 sText_HiDoSomethingAgainFemale[] = _("{STR_VAR_1}: הו! {PLAYER}, שלום!\nתרצה לעשות משהו?");

const u8 *const gTexts_UR_HiDoSomething[][GENDER_COUNT] = {
    {
        sText_HiDoSomethingMale,
        sText_HiDoSomethingFemale
    }, {
        sText_HiDoSomethingAgainMale,
        sText_HiDoSomethingAgainFemale
    }
};

ALIGNED(4) static const u8 sText_DoSomethingMale[] = _("רוצה לעשות משהו?");
ALIGNED(4) static const u8 sText_DoSomethingFemale[] = _("תרצה לעשות משהו?");
ALIGNED(4) static const u8 sText_DoSomethingAgainMale[] = _("{STR_VAR_1}: מה תרצה לעשות\nעכשיו?");
ALIGNED(4) static const u8 sText_DoSomethingAgainFemale[] = _("{STR_VAR_1}‘また なにかする？");

// Unused
static const u8 *const sDoSomethingTexts[][GENDER_COUNT] = {
    {
        sText_DoSomethingMale,
        sText_DoSomethingFemale
    }, {
        sText_DoSomethingAgainMale,
        sText_DoSomethingAgainMale // was probably supposed to be sText_DoSomethingAgainFemale
    }
};

ALIGNED(4) static const u8 sText_SomebodyHasContactedYou[] = _("מישהו יצר איתך קשר.{PAUSE 60}");
ALIGNED(4) static const u8 sText_PlayerHasContactedYou[] = _("{STR_VAR_1} יצר איתך קשר.{PAUSE 60}");

const u8 *const gTexts_UR_PlayerContactedYou[] = {
    sText_SomebodyHasContactedYou,
    sText_PlayerHasContactedYou
};

ALIGNED(4) static const u8 sText_AwaitingResponseFromTrainer[] = _("ממתין לתשובה\nמהמאמן השני…");
ALIGNED(4) static const u8 sText_AwaitingResponseFromPlayer[] = _("ממתין לתשובה\nמ{STR_VAR_1}…");

const u8 *const gTexts_UR_AwaitingResponse[] = {
    sText_AwaitingResponseFromTrainer,
    sText_AwaitingResponseFromPlayer
};

ALIGNED(4) static const u8 sText_AwaitingResponseCancelBButton[] = _("あいての ていあんを まっています\nビーボタンで キャンセル");

ALIGNED(4) const u8 gText_UR_ShowTrainerCard[] = _("המאמן השני הראה לך\nאת כרטיס המאמן שלו.\pתרצה להראות את כרטיס\nהמאמן שלך?");
ALIGNED(4) const u8 gText_UR_BattleChallenge[] = _("המאמן השני מזמין אותך\nלקרב.\pתקבל את ההזמנה\nלקרב?");
ALIGNED(4) const u8 gText_UR_ChatInvitation[] = _("המאמן השני מזמין אותך\nלצ'אט.\pתקבל את ההזמנה\nלצ'אט?");
ALIGNED(4) const u8 gText_UR_OfferToTradeMon[] = _("יש הצעה להחליף את\n{DYNAMIC 1} ברמה {DYNAMIC 0} שרשמת\pתמורת {DYNAMIC 3}\nברמה {DYNAMIC 2}.\pתקבל את הצעת\nההחלפה?");
ALIGNED(4) const u8 gText_UR_OfferToTradeEgg[] = _("יש הצעה להחליף את\nהביצה שרשמת.\lתקבל את הצעת ההחלפה?");
ALIGNED(4) const u8 gText_UR_ChatDropped[] = _("הצ'אט נותק.\p");
ALIGNED(4) const u8 gText_UR_OfferDeclined1[] = _("דחית את ההצעה.\p");
ALIGNED(4) const u8 gText_UR_OfferDeclined2[] = _("דחית את ההצעה.\p");
ALIGNED(4) const u8 gText_UR_ChatEnded[] = _("הצ'אט הסתיים.\p");

// Unused
static const u8 *const sInvitationTexts[] = {
    gText_UR_ShowTrainerCard,
    gText_UR_BattleChallenge,
    gText_UR_ChatInvitation,
    gText_UR_OfferToTradeMon
};

ALIGNED(4) static const u8 sText_JoinChatMale[] = _("הו, היי! אנחנו בצ'אט כרגע.\nרוצה להצטרף אלינו?");
ALIGNED(4) static const u8 sText_PlayerJoinChatMale[] = _("{STR_VAR_1}: היי, {PLAYER}!\nאנחנו בצ'אט כרגע.\lרוצה להצטרף אלינו?");
ALIGNED(4) static const u8 sText_JoinChatFemale[] = _("הו, שלום! אנחנו בצ'אט עכשיו.\nתרצה להצטרף אלינו?");
ALIGNED(4) static const u8 sText_PlayerJoinChatFemale[] = _("{STR_VAR_1}: הו, שלום, {PLAYER}!\nאנחנו בצ'אט עכשיו.\lתרצה להצטרף אלינו?");

const u8 *const gTexts_UR_JoinChat[][GENDER_COUNT] = {
    {
        sText_JoinChatMale,
        sText_JoinChatFemale
    }, {
        sText_PlayerJoinChatMale,
        sText_PlayerJoinChatFemale
    }
};

ALIGNED(4) const u8 gText_UR_TrainerAppearsBusy[] = _("……\nנראה שהמאמן עסוק…\p");
ALIGNED(4) static const u8 sText_WaitForBattleMale[] = _("קרב, הא?\nבסדר, רק תן לי קצת זמן.");
ALIGNED(4) static const u8 sText_WaitForChatMale[] = _("אתה רוצה לשוחח, הא?\nבטח, רק חכה רגע.");
ALIGNED(4) static const u8 sText_ShowTrainerCardMale[] = _("בטח! כברכת “שלום” שלי,\nהנה כרטיס המאמן שלי.");
ALIGNED(4) static const u8 sText_WaitForBattleFemale[] = _("קרב? כמובן, אבל אני צריך\nזמן להתכונן.");
ALIGNED(4) static const u8 sText_WaitForChatFemale[] = _("רצית לשוחח?\nבסדר, אבל חכה רגע.");
ALIGNED(4) static const u8 sText_ShowTrainerCardFemale[] = _("כהיכרות, אראה לך את\nכרטיס המאמן שלי.");

const u8 *const gTexts_UR_WaitOrShowCard[GENDER_COUNT][4] = {
    {
        sText_WaitForBattleMale,
        sText_WaitForChatMale,
        NULL,
        sText_ShowTrainerCardMale
    }, {
        sText_WaitForBattleFemale,
        sText_WaitForChatFemale,
        NULL,
        sText_ShowTrainerCardFemale
    }
};

ALIGNED(4) static const u8 sText_WaitForChatMale2[] = _("チャットだね！\nわかった ちょっと まってて！");
ALIGNED(4) static const u8 sText_DoneWaitingBattleMale[] = _("תודה שחיכית!\nבוא נתחיל את הקרב!{PAUSE 60}");
ALIGNED(4) static const u8 sText_DoneWaitingChatMale[] = _("בסדר גמור!\nבוא נשוחח!{PAUSE 60}");
ALIGNED(4) static const u8 sText_DoneWaitingBattleFemale[] = _("סליחה שהמתנת!\nבוא נתחיל!{PAUSE 60}");
ALIGNED(4) static const u8 sText_DoneWaitingChatFemale[] = _("סליחה שהמתנת!\nבוא נשוחח.{PAUSE 60}");
ALIGNED(4) static const u8 sText_TradeWillBeStarted[] = _("ההחלפה תתחיל.{PAUSE 60}");
ALIGNED(4) static const u8 sText_BattleWillBeStarted[] = _("הקרב יתחיל.{PAUSE 60}");
ALIGNED(4) static const u8 sText_EnteringChat[] = _("נכנס לצ'אט…{PAUSE 60}");

const u8 *const gTexts_UR_StartActivity[][GENDER_COUNT][3] = {
    {
        {
            sText_BattleWillBeStarted,
            sText_EnteringChat,
            sText_TradeWillBeStarted
        }, {
            sText_BattleWillBeStarted,
            sText_EnteringChat,
            sText_TradeWillBeStarted
        }
    }, {
        {
            sText_DoneWaitingBattleMale,
            sText_DoneWaitingChatMale,
            sText_TradeWillBeStarted
        }, {
            sText_DoneWaitingBattleFemale,
            sText_DoneWaitingChatFemale,
            sText_TradeWillBeStarted
        }
    }
};

ALIGNED(4) static const u8 sText_BattleDeclinedMale[] = _("סליחה! נראה שהפוקימונים\nשלי לא מרגישים טוב כרגע.\lנילחם בפעם אחרת.\p");
ALIGNED(4) static const u8 sText_BattleDeclinedFemale[] = _("אני מצטער מאוד, אבל\nהפוקימונים שלי לא מרגישים טוב…\pבוא נילחם בפעם אחרת.\p");

const u8 *const gTexts_UR_BattleDeclined[GENDER_COUNT] = {
    sText_BattleDeclinedMale,
    sText_BattleDeclinedFemale
};

ALIGNED(4) static const u8 sText_ShowTrainerCardDeclinedMale[] = _("הא? כרטיס המאמן שלי…\nלאן הוא נעלם?\lסליחה! אראה לך בפעם אחרת!\p");
ALIGNED(4) static const u8 sText_ShowTrainerCardDeclinedFemale[] = _("הו? איפה שמתי את כרטיס\nהמאמן שלי?…\lסליחה! אראה לך אחר כך!\p");

const u8 *const gTexts_UR_ShowTrainerCardDeclined[GENDER_COUNT] = {
    sText_ShowTrainerCardDeclinedMale,
    sText_ShowTrainerCardDeclinedFemale
};

ALIGNED(4) static const u8 sText_IfYouWantToDoSomethingMale[] = _("אם תרצה לעשות איתי\nמשהו, פשוט תקרא לי!\p");
ALIGNED(4) static const u8 sText_IfYouWantToDoSomethingFemale[] = _("אם תרצה לעשות איתי\nמשהו, אל תתבייש.\p");

const u8 *const gTexts_UR_IfYouWantToDoSomething[GENDER_COUNT] = {
    sText_IfYouWantToDoSomethingMale,
    sText_IfYouWantToDoSomethingFemale
};

ALIGNED(4) const u8 gText_UR_TrainerBattleBusy[] = _("אופס! סליחה, אבל אני\nצריך לעשות משהו אחר.\lבפעם אחרת, בסדר?\p");
ALIGNED(4) const u8 gText_UR_NeedTwoMonsOfLevel30OrLower1[] = _("כדי להילחם דרושים לך\nשני פוקימונים מתחת\lלרמה 03.\p");
ALIGNED(4) const u8 gText_UR_NeedTwoMonsOfLevel30OrLower2[] = _("לקרב דרושים שני\nפוקימונים מתחת לרמה 03.\p");

ALIGNED(4) static const u8 sText_DeclineChatMale[] = _("הו, בסדר.\nבוא לראות אותי מתי שתרצה.\p");
ALIGNED(4) static const u8 stext_DeclineChatFemale[] = _("הו…\nאנא בוא מתי שתרצה.\p");

// Response from partner when player declines chat
const u8 *const gTexts_UR_DeclineChat[GENDER_COUNT] = {
    sText_DeclineChatMale,
    stext_DeclineChatFemale
};

ALIGNED(4) static const u8 sText_ChatDeclinedMale[] = _("הו, סליחה!\nאני פשוט לא יכול ממש עכשיו.\lנשוחח בפעם אחרת.\p");
ALIGNED(4) static const u8 sText_ChatDeclinedFemale[] = _("הו, אני מצטער.\nיש לי יותר מדי לעשות עכשיו.\lנשוחח בפעם אחרת.\p");

// Response from partner when they decline chat
const u8 *const gTexts_UR_ChatDeclined[GENDER_COUNT] = {
    sText_ChatDeclinedMale,
    sText_ChatDeclinedFemale
};

ALIGNED(4) static const u8 sText_YoureToughMale[] = _("וואו!\nאני רואה שאתה די חזק!\p");
ALIGNED(4) static const u8 sText_UsedGoodMoveMale[] = _("השתמשת במהלך הזה?\nזו אסטרטגיה טובה!\p");
ALIGNED(4) static const u8 sText_BattleSurpriseMale[] = _("כל הכבוד!\nזה היה פותח עיניים!\p");
ALIGNED(4) static const u8 sText_SwitchedMonsMale[] = _("הו! איך יכולת להשתמש\nבפוקימון הזה במצב כזה?\p");
ALIGNED(4) static const u8 sText_YoureToughFemale[] = _("הפוקימון הזה…\nהוא גודל ממש טוב!\p");
ALIGNED(4) static const u8 sText_UsedGoodMoveFemale[] = _("זהו זה!\nזה המהלך הנכון עכשיו!\p");
ALIGNED(4) static const u8 sText_BattleSurpriseFemale[] = _("זה מדהים!\nאפשר להילחם ככה?\p");
ALIGNED(4) static const u8 sText_SwitchedMonsFemale[] = _("יש לך תזמון מצוין\nלהחלפת פוקימונים!\p");

const u8 *const gTexts_UR_BattleReaction[GENDER_COUNT][4] = {
    {
        sText_YoureToughMale,
        sText_UsedGoodMoveMale,
        sText_BattleSurpriseMale,
        sText_SwitchedMonsMale
    }, {
        sText_YoureToughFemale,
        sText_UsedGoodMoveFemale,
        sText_BattleSurpriseFemale,
        sText_SwitchedMonsFemale
    }
};

ALIGNED(4) static const u8 sText_LearnedSomethingMale[] = _("הו, אני מבין!\nזה מלמד!\p");
ALIGNED(4) static const u8 sText_ThatsFunnyMale[] = _("אל תגיד עוד משהו מצחיק!\nכואב לי מרוב צחוק!\p");
ALIGNED(4) static const u8 sText_RandomChatMale1[] = _("הו?\nמשהו כזה קרה.\p");
ALIGNED(4) static const u8 sText_RandomChatMale2[] = _("הממ… מה?\nאז זה מה שאתה אומר?\p");
ALIGNED(4) static const u8 sText_LearnedSomethingFemale[] = _("באמת?\nלא ידעתי את זה.\p");
ALIGNED(4) static const u8 sText_ThatsFunnyFemale[] = _("חחח!\nעל מה מדובר?\p");
ALIGNED(4) static const u8 sText_RandomChatFemale1[] = _("כן, בדיוק!\nזה מה שהתכוונתי.\p");
ALIGNED(4) static const u8 sText_RandomChatFemale2[] = _("במילים אחרות…\nכן! נכון!\p");

const u8 *const gTexts_UR_ChatReaction[GENDER_COUNT][4] = {
    {
        sText_LearnedSomethingMale,
        sText_ThatsFunnyMale,
        sText_RandomChatMale1,
        sText_RandomChatMale2
    }, {
        sText_LearnedSomethingFemale,
        sText_ThatsFunnyFemale,
        sText_RandomChatFemale1,
        sText_RandomChatFemale2
    }
};

ALIGNED(4) static const u8 sText_ShowedTrainerCardMale1[] = _("אני רק מראה את כרטיס\nהמאמן שלי כברכת שלום.\p");
ALIGNED(4) static const u8 sText_ShowedTrainerCardMale2[] = _("אני מקווה להכיר אותך יותר!\p");
ALIGNED(4) static const u8 sText_ShowedTrainerCardFemale1[] = _("אנחנו מראים זה לזה את\nכרטיסי המאמן כדי להכיר.\p");
ALIGNED(4) static const u8 sText_ShowedTrainerCardFemale2[] = _("נעים להכיר.\nאל תהיה זר!\p");

const u8 *const gTexts_UR_TrainerCardReaction[GENDER_COUNT][2] = {
    {
        sText_ShowedTrainerCardMale1,
        sText_ShowedTrainerCardMale2
    }, {
        sText_ShowedTrainerCardFemale1,
        sText_ShowedTrainerCardFemale2
    }
};

ALIGNED(4) static const u8 sText_MaleTraded1[] = _("יש!\nממש רציתי את הפוקימון הזה!\p");
ALIGNED(4) static const u8 sText_MaleTraded2[] = _("סוף סוף, החלפה השיגה לי\nאת הפוקימון שרציתי מזמן.\p");
ALIGNED(4) static const u8 sText_FemaleTraded1[] = _("אני מחליף פוקימונים כרגע.\p");
ALIGNED(4) static const u8 sText_FemaleTraded2[] = _("סוף סוף השגתי בהחלפה את\nהפוקימון שרציתי!\p");

const u8 *const gTexts_UR_TradeReaction[GENDER_COUNT][4] = {
    {
        sText_MaleTraded1,
        sText_MaleTraded2
    }, {
        sText_FemaleTraded1,
        sText_FemaleTraded2
    }
};

const u8 gText_UR_XCheckedTradingBoard[] = _("{STR_VAR_1} בדק את\nלוח ההחלפות.\p");
ALIGNED(4) const u8 gText_UR_RegisterMonAtTradingBoard[] = _("ברוך הבא ללוח ההחלפות.\pאפשר לרשום את הפוקימון\nשלך ולהציע אותו להחלפה.\pתרצה לרשום אחד\nמהפוקימונים שלך?");
ALIGNED(4) const u8 gText_UR_TradingBoardInfo[] = _("לוח ההחלפות הזה משמש\n"
                                                    "להצעת פוקימון להחלפה.\p"
                                                    "כל שעליך לעשות הוא לרשום\n"
                                                    "פוקימון להחלפה.\p"
                                                    "מאמן אחר עשוי להציע פוקימון\n"
                                                    "מהקבוצה שלו בתמורה.\p"
                                                    "אנחנו מקווים שתרשום\n"
                                                    "פוקימונים ותחליף אותם עם\l"
                                                    "מאמנים רבים.\p"
                                                    "תרצה לרשום אחד\n"
                                                    "מהפוקימונים שלך?");
ALIGNED(4) static const u8 sText_ThankYouForRegistering[] = _("こうかんけいじばん の とうろくが\nかんりょう しました\pごりよう ありがとう\nございました！\p");
ALIGNED(4) static const u8 sText_NobodyHasRegistered[] = _("けいじばんに だれも ポケモンを\nとうろく していません\p\n");
ALIGNED(4) const u8 gText_UR_ChooseRequestedMonType[] = _("אנא בחר את סוג הפוקימון\nשתרצה לקבל בהחלפה.\n");
ALIGNED(4) const u8 gText_UR_WhichMonWillYouOffer[] = _("איזה פוקימון מהקבוצה שלך\nתציע בהחלפה?\p");
ALIGNED(4) const u8 gText_UR_RegistrationCanceled[] = _("הרישום בוטל.\p");
ALIGNED(4) const u8 gText_UR_RegistraionCompleted[] = _("הרישום הושלם.\p");
ALIGNED(4) const u8 gText_UR_TradeCanceled[] = _("ההחלפה בוטלה.\p");
ALIGNED(4) const u8 gText_UR_CancelRegistrationOfMon[] = _("לבטל את רישום {STR_VAR_1}\nשלך ברמה {STR_VAR_2}?");
ALIGNED(4) const u8 gText_UR_CancelRegistrationOfEgg[] = _("לבטל את רישום הביצה\nשלך?");
ALIGNED(4) const u8 gText_UR_RegistrationCanceled2[] = _("הרישום בוטל.\p");
ALIGNED(4) static const u8 sText_TradeTrainersWillBeListed[] = _("こうかんを きぼうしているひとを\nひょうじします");
ALIGNED(4) static const u8 sText_ChooseTrainerToTradeWith2[] = _("こうかん したい トレーナーを\nえらんで ください");
ALIGNED(4) const u8 gText_UR_AskTrainerToMakeTrade[] = _("תרצה לבקש מ{STR_VAR_1}\nלבצע החלפה?");
ALIGNED(4) static const u8 sText_AwaitingResponseFromTrainer2[] = _("……\nあいての へんじを まっています");
ALIGNED(4) static const u8 sText_NotRegisteredAMonForTrade[] = _("あなたが こうかんにだす\nポケモンが とうろくされていません\p");
ALIGNED(4) const u8 gText_UR_DontHaveTypeTrainerWants[] = _("אין לך פוקימון מסוג\n{STR_VAR_2} ש{STR_VAR_1} רוצה.\p");
ALIGNED(4) const u8 gText_UR_DontHaveEggTrainerWants[] = _("אין לך ביצה\nש{STR_VAR_1} רוצה.\p");

ALIGNED(4) static const u8 sText_PlayerCantTradeForYourMon[] = _("{STR_VAR_1} לא יכול להחליף\nעם הפוקימון שלך כרגע.\p");
ALIGNED(4) static const u8 sText_CantTradeForPartnersMon[] = _("אי אפשר להחליף עם\nהפוקימון של {STR_VAR_1} כרגע.\p");

// Unused
static const u8 *const sCantTradeMonTexts[] = {
    sText_PlayerCantTradeForYourMon,
    sText_CantTradeForPartnersMon
};

ALIGNED(4) const u8 gText_UR_TradeOfferRejected[] = _("הצעת ההחלפה שלך נדחתה.\p");
ALIGNED(4) const u8 gText_UR_EggTrade[] = _("החלפת ביצה");
ALIGNED(4) const u8 gText_UR_ChooseJoinCancel[] = _("{DPAD_UPDOWN}בחר  {A_BUTTON}הצטרף  {B_BUTTON}ביטול");
ALIGNED(4) const u8 gText_UR_ChooseTrainer[] = _("אנא בחר מאמן.");
ALIGNED(4) static const u8 sText_ChooseTrainerSingleBattle[] = _("אנא בחר מאמן\nלקרב יחיד.");
ALIGNED(4) static const u8 sText_ChooseTrainerDoubleBattle[] = _("אנא בחר מאמן\nלקרב כפול.");
ALIGNED(4) static const u8 sText_ChooseLeaderMultiBattle[] = _("אנא בחר מנהיג\nלקרב מרובה.");
ALIGNED(4) static const u8 sText_ChooseTrainerToTradeWith[] = _("אנא בחר את המאמן\nלהחלפה.");
ALIGNED(4) static const u8 sText_ChooseTrainerToShareWonderCards[] = _("אנא בחר את המאמן\nשמשתף כרטיסי פלא.");
ALIGNED(4) static const u8 sText_ChooseTrainerToShareWonderNews[] = _("אנא בחר את המאמן\nשמשתף חדשות פלא.");
ALIGNED(4) static const u8 sText_ChooseLeaderPokemonJump[] = _("קפצו עם פוקימונים קטנים!\nאנא בחר מנהיג.");
ALIGNED(4) static const u8 sText_ChooseLeaderBerryCrush[] = _("מועך הפירות!\nאנא בחר מנהיג.");
ALIGNED(4) static const u8 sText_ChooseLeaderBerryPicking[] = _("קטיף הפירות של דודריו!\nאנא בחר מנהיג.");

const u8 *const gTexts_UR_ChooseTrainer[] = {
    [LINK_GROUP_SINGLE_BATTLE] = sText_ChooseTrainerSingleBattle,
    [LINK_GROUP_DOUBLE_BATTLE] = sText_ChooseTrainerDoubleBattle,
    [LINK_GROUP_MULTI_BATTLE]  = sText_ChooseLeaderMultiBattle,
    [LINK_GROUP_TRADE]         = sText_ChooseTrainerToTradeWith,
    [LINK_GROUP_POKEMON_JUMP]  = sText_ChooseLeaderPokemonJump,
    [LINK_GROUP_BERRY_CRUSH]   = sText_ChooseLeaderBerryCrush,
    [LINK_GROUP_BERRY_PICKING] = sText_ChooseLeaderBerryPicking,
    [LINK_GROUP_WONDER_CARD]   = sText_ChooseTrainerToShareWonderCards,
    [LINK_GROUP_WONDER_NEWS]   = sText_ChooseTrainerToShareWonderNews
};

ALIGNED(4) const u8 gText_UR_SearchingForWirelessSystemWait[] = _("מחפש מערכת תקשורת\nאלחוטית. המתן...");
ALIGNED(4) static const u8 sText_MustHaveTwoMonsForDoubleBattle[] = _("ダブルバトルでは 2ひき いじょうの\nポケモンが ひつようです\p");
ALIGNED(4) const u8 gText_UR_AwaitingPlayersResponse[] = _("ממתין לתשובת {STR_VAR_1}…");
ALIGNED(4) const u8 gText_UR_PlayerHasBeenAskedToRegisterYouPleaseWait[] = _("{STR_VAR_1} התבקש לרשום\nאותך כחבר קבוצה. המתן.");
ALIGNED(4) const u8 gText_UR_AwaitingResponseFromWirelessSystem[] = _("ממתין לתשובה ממערכת\nהתקשורת האלחוטית.");
ALIGNED(4) static const u8 sText_PleaseWaitForOtherTrainersToGather[] = _("ほかの さんかしゃが そろうまで\nしょうしょう おまちください");

ALIGNED(4) static const u8 sText_NoCardsSharedRightNow[] = _("נראה שאין כרטיסים\nמשותפים כרגע.");
ALIGNED(4) static const u8 sText_NoNewsSharedRightNow[] = _("נראה שאין חדשות\nמשותפות כרגע.");

const u8 *const gTexts_UR_NoWonderShared[] = {
    sText_NoCardsSharedRightNow,
    sText_NoNewsSharedRightNow
};

ALIGNED(4) const u8 gText_UR_Battle[] = _("קרב");
ALIGNED(4) const u8 gText_UR_Chat2[] = _("צ'אט");
ALIGNED(4) const u8 gText_UR_Greetings[] = _("ברכות");
ALIGNED(4) const u8 gText_UR_Exit[] = _("יציאה");

ALIGNED(4) const u8 gText_UR_Exit2[] = _("יציאה");
ALIGNED(4) const u8 gText_UR_Info[] = _("מידע");
ALIGNED(4) const u8 gText_UR_NameWantedOfferLv[] = _("שם{CLEAR_TO 0x3C}מבוקש{CLEAR_TO 0x6E}מוצע{CLEAR_TO 0xC6}רמה");

ALIGNED(4) const u8 gText_UR_SingleBattle[] = _("קרב יחיד");
ALIGNED(4) const u8 gText_UR_DoubleBattle[] = _("קרב כפול");
ALIGNED(4) const u8 gText_UR_MultiBattle[] = _("קרב מרובה");
ALIGNED(4) const u8 gText_UR_PokemonTrades[] = _("החלפות פוקימון");
ALIGNED(4) const u8 gText_UR_Chat[] = _("צ'אט");
ALIGNED(4) const u8 gText_UR_Cards[] = _("כרטיסים");
ALIGNED(4) const u8 gText_UR_WonderCards[] = _("כרטיסי פלא");
ALIGNED(4) const u8 gText_UR_WonderNews[] = _("חדשות פלא");
ALIGNED(4) const u8 gText_UR_PokemonJump[] = _("קפיצת פוקימון");
ALIGNED(4) const u8 gText_UR_BerryCrush[] = _("מועך פירות");
ALIGNED(4) const u8 gText_UR_BerryPicking[] = _("קטיף פירות");
ALIGNED(4) const u8 gText_UR_Search[] = _("חיפוש");
ALIGNED(4) const u8 gText_UR_SpinTrade[] = _("החלפה מסתובבת");
ALIGNED(4) const u8 gText_UR_ItemTrade[] = _("החלפת פריטים");

ALIGNED(4) static const u8 sText_ItsNormalCard[] = _("זהו כרטיס רגיל.");
ALIGNED(4) static const u8 sText_ItsBronzeCard[] = _("זהו כרטיס ארד!");
ALIGNED(4) static const u8 sText_ItsCopperCard[] = _("זהו כרטיס נחושת!");
ALIGNED(4) static const u8 sText_ItsSilverCard[] = _("זהו כרטיס כסף!");
ALIGNED(4) static const u8 sText_ItsGoldCard[] = _("זהו כרטיס זהב!");

const u8 *const gTexts_UR_CardColor[] = {
    sText_ItsNormalCard,
    sText_ItsBronzeCard,
    sText_ItsCopperCard,
    sText_ItsSilverCard,
    sText_ItsGoldCard
};

ALIGNED(4) const u8 gText_UR_TrainerCardInfoPage1[] = _("זהו כרטיס המאמן של\n{DYNAMIC 0} {DYNAMIC 1}…\l{DYNAMIC 2}\pפוקדקס: {DYNAMIC 3}\nזמן:    {DYNAMIC 4}:{DYNAMIC 5}\p");
ALIGNED(4) const u8 gText_UR_TrainerCardInfoPage2[] = _("קרבות: {DYNAMIC 0} נצחונות  {DYNAMIC 2} הפסדים\nהחלפות:  {DYNAMIC 3} פעמים\p“{DYNAMIC 4} {DYNAMIC 5}\n{DYNAMIC 6} {DYNAMIC 7}”\p");
ALIGNED(4) static const u8 sText_GladToMeetYouMale[] = _("{DYNAMIC 1}: שמח שנפגשנו!{PAUSE 60}");
ALIGNED(4) static const u8 sText_GladToMeetYouFemale[] = _("{DYNAMIC 1}: נעים להכיר!{PAUSE 60}");

const u8 *const gTexts_UR_GladToMeetYou[GENDER_COUNT] = {
    sText_GladToMeetYouMale,
    sText_GladToMeetYouFemale
};

ALIGNED(4) const u8 gText_UR_FinishedCheckingPlayersTrainerCard[] = _("סיימת לעיין בכרטיס המאמן\nשל {DYNAMIC 1}.{PAUSE 60}");
ALIGNED(4) static const u8 sText_CanceledReadingCard[] = _("הקריאה בכרטיס בוטלה.");

static const struct MysteryGiftClientCmd sClientScript_DynamicError[] = {
    {CLI_RECV, MG_LINKID_DYNAMIC_MSG},
    {CLI_COPY_MSG},
    {CLI_SEND_READY_END},
    {CLI_RETURN, CLI_MSG_BUFFER_FAILURE}
};

const struct MysteryGiftServerCmd gServerScript_ClientCanceledCard[] = {
    {SVR_LOAD_CLIENT_SCRIPT, PTR_ARG(sClientScript_DynamicError)},
    {SVR_SEND},
    {SVR_LOAD_MSG, PTR_ARG(sText_CanceledReadingCard)},
    {SVR_SEND},
    {SVR_RECV, MG_LINKID_READY_END},
    {SVR_RETURN, SVR_MSG_CLIENT_CANCELED}
};
