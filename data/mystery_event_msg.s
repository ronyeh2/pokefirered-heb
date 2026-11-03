@ These are event scripts. They should not be moved to C.

#include "constants/global.h"
#include "constants/flags.h"
#include "constants/moves.h"
#include "constants/songs.h"
#include "constants/species.h"
#include "constants/vars.h"
#include "constants/items.h"
#include "constants/region_map_sections.h"
	.include "asm/macros.inc"
	.include "asm/macros/event.inc"
	.include "constants/constants.inc"

	.section .rodata
	
	.align 2
MysteryEventScript_StampCard::
	setvaddress MysteryEventScript_StampCard
	setorcopyvar VAR_RESULT, 1
	specialvar VAR_0x8008, GetMysteryGiftCardStat
	setorcopyvar VAR_RESULT, 0
	specialvar VAR_0x8009, GetMysteryGiftCardStat
	subvar VAR_0x8008, VAR_0x8009
	buffernumberstring STR_VAR_1, VAR_0x8008
	lock
	faceplayer
	vmessage sText_MysteryGiftStampCard
	waitmessage
	waitbuttonpress
	release
	end

sText_MysteryGiftStampCard:
	.string "תודה שהשתמשת במערכת\n"
	.string "כרטיס החותמות.\p"
	.string "נותרו לך עוד {STR_VAR_1} חותמות\n"
	.string "כדי למלא את הכרטיס.$"

MysteryEventScript_SurfPichu::
	setvaddress MysteryEventScript_SurfPichu
	vgoto_if_unset FLAG_MYSTERY_GIFT_DONE, SurfPichu_GiveIfPossible
	returnram

SurfPichu_GiveIfPossible:
	specialvar VAR_EVENT_PICHU_SLOT, CalculatePlayerPartyCount
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, PARTY_SIZE, SurfPichu_FullParty
	setflag FLAG_MYSTERY_GIFT_DONE
	vcall SurfPichu_GiveEgg
	lock
	faceplayer
	vmessage sText_MysteryGiftEgg
	waitmessage
	waitbuttonpress
	playfanfare MUS_OBTAIN_ITEM
	waitfanfare
	release
	end

SurfPichu_FullParty:
	lock
	faceplayer
	vmessage sText_FullParty
	waitmessage
	waitbuttonpress
	release
	end

SurfPichu_GiveEgg:
	giveegg SPECIES_PICHU
	setmonmodernfatefulencounter VAR_EVENT_PICHU_SLOT
	setmonmetlocation VAR_EVENT_PICHU_SLOT, METLOC_FATEFUL_ENCOUNTER
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, 1, SurfPichu_Slot1
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, 2, SurfPichu_Slot2
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, 3, SurfPichu_Slot3
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, 4, SurfPichu_Slot4
	vgoto_if_eq VAR_EVENT_PICHU_SLOT, 5, SurfPichu_Slot5
	return

SurfPichu_Slot1:
	setmonmove 1, 2, MOVE_SURF
	return

SurfPichu_Slot2:
	setmonmove 2, 2, MOVE_SURF
	return

SurfPichu_Slot3:
	setmonmove 3, 2, MOVE_SURF
	return

SurfPichu_Slot4:
	setmonmove 4, 2, MOVE_SURF
	return

SurfPichu_Slot5:
	setmonmove 5, 2, MOVE_SURF
	return

sText_MysteryGiftEgg:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "ממרכז הפוקימון יש לנו\n"
	.string "מתנה עבורך - ביצת פוקימון!\p"
	.string "אנא גדל אותה באהבה\n"
	.string "ובעדינות.$"

sText_FullParty:
	.string "אוי, נראה שהקבוצה שלך מלאה.\p"
	.string "אנא בוא לראות אותי אחרי\n"
	.string "שתאחסן פוקימון במחשב.$"

MysteryEventScript_VisitingTrainer::
	setvaddress MysteryEventScript_VisitingTrainer
	special ValidateEReaderTrainer
	vgoto_if_eq VAR_RESULT, 0, MysteryEventScript_VisitingTrainerArrived
	lock
	faceplayer
	vmessage sText_MysteryGiftVisitingTrainer
	waitmessage
	waitbuttonpress
	release
	end

MysteryEventScript_VisitingTrainerArrived:
	lock
	faceplayer
	vmessage sText_MysteryGiftVisitingTrainer_2
	waitmessage
	waitbuttonpress
	release
	end

sText_MysteryGiftVisitingTrainer:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "בעזרת כרטיס הפלא הזה תוכל\n"
	.string "להשתתף בסקר בחנות\l"
	.string "הפוקימונים.\p"
	.string "השתמש בסקרים כדי להזמין\n"
	.string "מאמנים לאיי סביי.\p"
	.string "…תן לי לתת לך סיסמה\n"
	.string "סודית לסקר:\p"
	.string "“תנו לי\n"
	.string "מאמן מדהים”\p"
	.string "כתוב אותה בסקר ושלח אותה\n"
	.string "אל מערכת התקשורת\l"
	.string "האלחוטית.$"

sText_MysteryGiftVisitingTrainer_2:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "מאמן הגיע לאיי סביי\n"
	.string "ומחפש אותך.\p"
	.string "אנחנו מקווים שתיהנה\n"
	.string "מהקרב מול המאמן האורח.\p"
	.string "תוכל להזמין מאמנים נוספים\n"
	.string "על ידי הזנת סיסמאות אחרות.\p"
	.string "נסה לחפש סיסמאות נוספות\n"
	.string "שעשויות לעבוד.$"

MysteryEventScript_BattleCard::
	setvaddress MysteryEventScript_BattleCard
	vgoto_if_set FLAG_MYSTERY_GIFT_DONE, MysteryEventScript_BattleCardInfo
	setorcopyvar VAR_RESULT, 2
	specialvar VAR_0x8008, GetMysteryGiftCardStat
	vgoto_if_ne VAR_0x8008, 3, MysteryEventScript_BattleCardInfo
	lock
	faceplayer
	vmessage sText_MysteryGiftBattleCountCard_2
	waitmessage
	waitbuttonpress
	giveitem ITEM_POTION
	release
	setflag FLAG_MYSTERY_GIFT_DONE
	end

MysteryEventScript_BattleCardInfo:
	lock
	faceplayer
	vmessage sText_MysteryGiftBattleCountCard
	waitmessage
	waitbuttonpress
	release
	end

sText_MysteryGiftBattleCountCard:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "כרטיס מניין הקרבות עוקב\n"
	.string "אחרי מאזן הקרבות שלך מול\l"
	.string "מאמנים עם אותו כרטיס.\p"
	.string "חפש והילחם במאמנים שיש\n"
	.string "להם אותו כרטיס כמו שלך.\p"
	.string "תוכל לבדוק את הדירוג הכללי\n"
	.string "בקריאת החדשות.\p"
	.string "אנא נסה את זה!$"

sText_MysteryGiftBattleCountCard_2:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "ברכותיי!\p"
	.string "זכית בפרס על ניצחון\n"
	.string "בשלושה קרבות!\p"
	.string "אנחנו מקווים שזה יעודד\n"
	.string "אותך להילחם עוד.$"

MysteryEventScript_AuroraTicket::
	setvaddress MysteryEventScript_AuroraTicket
	lock
	faceplayer
	vgoto_if_set FLAG_RECEIVED_AURORA_TICKET, AuroraTicket_Obtained
	vgoto_if_set FLAG_FOUGHT_DEOXYS, AuroraTicket_Obtained
	checkitem ITEM_AURORA_TICKET, 1
	vgoto_if_eq VAR_RESULT, TRUE, AuroraTicket_Obtained
	vmessage sText_AuroraTicket1
	waitmessage
	waitbuttonpress
	checkitemspace ITEM_AURORA_TICKET, 1
	vgoto_if_eq VAR_RESULT, FALSE, AuroraTicket_NoBagSpace
	giveitem ITEM_AURORA_TICKET
	setflag FLAG_ENABLE_SHIP_BIRTH_ISLAND
	setflag FLAG_RECEIVED_AURORA_TICKET
	vmessage sText_AuroraTicket2
	waitmessage
	waitbuttonpress
	release
	end

AuroraTicket_NoBagSpace:
	vmessage sText_AuroraTicketNoPlace
	waitmessage
	waitbuttonpress
	release
	end

AuroraTicket_Obtained:
	vmessage sText_AuroraTicketGot
	waitmessage
	waitbuttonpress
	release
	end

sText_AuroraTicket1:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "אתה בטח {PLAYER}.\n"
	.string "יש כאן כרטיס עבורך.$"

sText_AuroraTicket2:
	.string "נראה שהוא מיועד לשימוש\n"
	.string "בנמל העיר ורמיליון.\p"
	.string "למה שלא תנסה ותראה\n"
	.string "במה מדובר?$"

sText_AuroraTicketGot:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.$"

sText_AuroraTicketNoPlace:
	.string "אוי, אני מצטער, {PLAYER}. תא\n"
	.string "פריטי המפתח בתיק שלך מלא.\p"
	.string "אנא אחסן משהו במחשב,\n"
	.string "ואז חזור לקחת את זה.$"

MysteryEventScript_MysticTicket::
	setvaddress MysteryEventScript_MysticTicket
	lock
	faceplayer
	vgoto_if_set FLAG_RECEIVED_MYSTIC_TICKET, MysticTicket_Obtained
	vgoto_if_set FLAG_FOUGHT_LUGIA, MysticTicket_Obtained
	vgoto_if_set FLAG_FOUGHT_HO_OH, MysticTicket_Obtained
	checkitem ITEM_MYSTIC_TICKET, 1
	vgoto_if_eq VAR_RESULT, TRUE, MysticTicket_Obtained
	vmessage sText_MysticTicket2
	waitmessage
	waitbuttonpress
	checkitemspace ITEM_MYSTIC_TICKET, 1
	vgoto_if_eq VAR_RESULT, FALSE, MysticTicket_NoBagSpace
	giveitem ITEM_MYSTIC_TICKET
	setflag FLAG_ENABLE_SHIP_NAVEL_ROCK
	setflag FLAG_RECEIVED_MYSTIC_TICKET
	vmessage sText_MysticTicket1
	waitmessage
	waitbuttonpress
	release
	end

MysticTicket_NoBagSpace:
	vmessage sText_MysticTicketNoPlace
	waitmessage
	waitbuttonpress
	release
	end

MysticTicket_Obtained:
	vmessage sText_MysticTicketGot
	waitmessage
	waitbuttonpress
	release
	end

sText_MysticTicket2:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "אתה בטח {PLAYER}.\n"
	.string "יש כאן כרטיס עבורך.$"

sText_MysticTicket1:
	.string "נראה שהוא מיועד לשימוש\n"
	.string "בנמל העיר ורמיליון.\p"
	.string "למה שלא תנסה ותראה\n"
	.string "במה מדובר?$"

sText_MysticTicketGot:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.$"

sText_MysticTicketNoPlace:
	.string "אוי, אני מצטער, {PLAYER}. תא\n"
	.string "פריטי המפתח בתיק שלך מלא.\p"
	.string "אנא אחסן משהו במחשב,\n"
	.string "ואז חזור לקחת את זה.$"

MysteryEventScript_AlteringCave::
	setvaddress MysteryEventScript_AlteringCave
	addvar VAR_ALTERING_CAVE_WILD_SET, 1
	vgoto_if_ne VAR_ALTERING_CAVE_WILD_SET, 10, MysteryEventScript_AlteringCave_
	setvar VAR_ALTERING_CAVE_WILD_SET, 0
MysteryEventScript_AlteringCave_:
	lock
	faceplayer
	vmessage sText_MysteryGiftAlteringCave
	waitmessage
	waitbuttonpress
	release
	end

sText_MysteryGiftAlteringCave:
	.string "תודה שהשתמשת במערכת\n"
	.string "מתנת מסתורין.\p"
	.string "לאחרונה יש שמועות על\n"
	.string "הופעות של פוקימונים נדירים.\p"
	.string "השמועות הן על מערת\n"
	.string "השינויים באי המנודים.\p"
	.string "למה שלא תבקר שם ותבדוק\n"
	.string "אם השמועות נכונות?$"
