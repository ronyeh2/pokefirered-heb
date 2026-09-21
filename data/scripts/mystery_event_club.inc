.equ GAVE_PROFILE,  VAR_TEMP_1

MysteryEventClub_EventScript_Woman::
	lock
	faceplayer
	goto_if_eq GAVE_PROFILE, TRUE, EventScript_AlreadyGaveProfile
	goto_if_set FLAG_SYS_SET_TRAINER_CARD_PROFILE, EventScript_GivenProfileBefore
	msgbox Text_IdLoveToHearYourProfile
	goto EventScript_AskForProfile
	end

EventScript_AlreadyGaveProfile:
	msgbox Text_TellMoreNextTime
	release
	end

EventScript_AskForProfile:
	message Text_TellMeWhatsYourProfile
	waitmessage
	multichoice 18, 6, MULTICHOICE_YES_NO_INFO_2, FALSE
	switch VAR_RESULT
	case 0, EventScript_AcceptGiveProfile
	case 1, EventScript_DeclineGiveProfile
	case 2, EventScript_ProfileInfo
	case SCR_MENU_CANCEL, EventScript_DeclineGiveProfile
	end

EventScript_ProfileInfo:
	msgbox Text_ExplainProfile
	goto EventScript_AskForProfile
	end

EventScript_AcceptGiveProfile:
	msgbox Text_WhatsYourProfile
	closemessage
	goto EventScript_GiveProfile
	end

EventScript_CancelGiveProfile:
	msgbox Text_DecidedNotTo
	release
	end

EventScript_GaveProfile:
	setvar GAVE_PROFILE, TRUE
	setvar VAR_0x8004, 0
	special ShowEasyChatMessage
	waitmessage
	delay 80
	msgbox Text_ProfileSaysSomethingAboutYou
	release
	end

EventScript_DeclineGiveProfile:
	msgbox Text_DontBeLikeThat
	release
	end

EventScript_GivenProfileBefore:
	msgbox Text_HiWeMeetAgain
	goto EventScript_AskForNewProfile
	end

EventScript_AskForNewProfile:
	message Text_ChangeYourProfile
	waitmessage
	multichoice 18, 6, MULTICHOICE_YES_NO_INFO_2, FALSE
	switch VAR_RESULT
	case 0, EventScript_AcceptGiveNewProfile
	case 1, EventScript_DeclineGiveNewProfile
	case 2, EventScript_ProfileInfo2
	case SCR_MENU_CANCEL, EventScript_DeclineGiveNewProfile
	end

EventScript_ProfileInfo2:
	msgbox Text_ExplainProfile
	goto EventScript_AskForNewProfile
	end

EventScript_AcceptGiveNewProfile:
	msgbox Text_WhatAreYouLikeNow
	closemessage
	goto EventScript_GiveProfile
	end

EventScript_DeclineGiveNewProfile:
	msgbox Text_LikeProfileWayItIs
	release
	end

EventScript_GaveSpecialProfile:
	setvar GAVE_PROFILE, TRUE
	setvar VAR_0x8004, 0
	special ShowEasyChatMessage
	waitmessage
	delay 80
	msgbox Text_HeardThatBefore
	release
	end

EventScript_GiveProfile:
	setvar VAR_0x8004, EASY_CHAT_TYPE_PROFILE
	call Common_ShowEasyChatScreen
	lock
	faceplayer
	goto_if_eq VAR_0x8004, 0, EventScript_GaveSpecialProfile
	goto_if_eq VAR_RESULT, FALSE, EventScript_CancelGiveProfile
	goto_if_eq VAR_RESULT, TRUE, EventScript_GaveProfile
	end

Text_IdLoveToHearYourProfile:
	.string "היי, נעים מאוד להכיר!\p"
	.string "…זה ממש לא נחמד מצדך.\n"
	.string "אולי תגיד גם אתה שלום?\p"
	.string "אז נו, ספר לי קצת\n"
	.string "על עצמך.\p"
	.string "בא לי לשמוע את הפרופיל שלך!$"

Text_TellMeWhatsYourProfile:
	.string "ספר לי משהו טוב על עצמך.\n"
	.string "מה הפרופיל שלך?$"

Text_ExplainProfile:
	.string "פרופיל נכתב בעזרת ארבע\n"
	.string "מילים או ביטויים.\p"
	.string "יש המון מילים לבחור מהן\n"
	.string "בשביל הפרופיל שלך.\p"
	.string "המילים והביטויים מסודרים\n"
	.string "בכמה קבוצות נוחות.\p"
	.string "קודם בוחרים קבוצה, ואז\n"
	.string "בוחרים מילה או ביטוי.\p"
	.string "…זה קל יותר ממה שזה נשמע.\n"
	.string "למה שלא תנסה?$"

Text_WhatsYourProfile:
	.string "מה הפרופיל שלך?$"

Text_DontBeLikeThat:
	.string "אוף… אל תהיה כזה.\n"
	.string "אתה יכול לספר לי את הפרופיל.$"

Text_DecidedNotTo:
	.string "אה, החלטת שלא בכל זאת?\n"
	.string "אתה ממש הפכפך, מה?$"

Text_HiWeMeetAgain:
	.string "היי!\n"
	.string "נפגשנו שוב!$"

Text_ChangeYourProfile:
	.string "רוצה לשנות את הפרופיל\n"
	.string "שלך?$"

Text_WhatAreYouLikeNow:
	.string "איזה בן אדם אתה עכשיו?\n"
	.string "ממש מעניין אותי לדעת.$"

Text_LikeProfileWayItIs:
	.string "בסדר, אתה אוהב את הפרופיל\n"
	.string "שלך כמו שהוא.\p"
	.string "גם אני חושבת ככה.$"

Text_ProfileSaysSomethingAboutYou:
	.string "הממ…\p"
	.string "הפרופיל שלך באמת מספר\n"
	.string "משהו על מי שאתה.\p"
	.string "עכשיו כשאני מכירה אותך יותר,\n"
	.string "אנחנו חברים טובים מתמיד!$"

Text_HeardThatBefore:
	.string "אה, כבר שמעתי את זה…\p"
	.string "נדמה לי שבן הדוד שלי,\n"
	.string "שגר רחוק, תמיד אמר את זה.$"

Text_TellMoreNextTime:
	.string "בפעם הבאה ספר לי עוד\n"
	.string "על עצמך, בבקשה!$"
