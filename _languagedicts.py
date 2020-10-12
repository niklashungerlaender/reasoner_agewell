buttons = {"back": dict(en="BACK", de="ZURÜCK", it="INDIETRO", nl="TERUG"),
           "add": dict(en="ADD", de="HINZUFÜGEN", it="AGGIUNGI", nl="VOEG TOE"),
           "cancel": dict(en="CANCEL", de="ABBRECHEN", it="CANCELLA", nl="ANNULEER"),
           "config  ": dict(en="CONFIG", de="KONFIGURIEREN", it="CONFIGURA", nl="CONFIGUREER"),
           "hard": dict(en="Too HARD", de="Zu SCHWER", it="Troppo DIFFICILE", nl="Te MOEILIJK"),
           "easy": dict(en="Too EASY", de="Zu LEICHT", it="Troppo FACILE", nl="Te MAKKELIJK"),
           "edit": dict(en="EDIT", de="EDITIEREN", it="PUBBLICA", nl="PAS AAN"),
           "like": dict(en="LIKE", de="LIKE", it="LIKE", nl="LIKE"),
           "next": dict(en="NEXT", de="WEITER", it="PROSSIMO", nl="VOLGENDE"),
           "ok": dict(en="OK", de="OK", it="OK", nl="OK"),
           "postpone": dict(en="POSTPONE", de="VERSCHIEBEN", it="RINVIA", nl="STEL UIT"),
           "thanks": dict(en="OK thank you", de="Ok, danke", it="OK grazie", nl="OK bedankt"),
           "didit": dict(en="YES I did it", de="Ja, ich hab es gemacht", it="Sì l'ho fatto",
                         nl="YES, Ik heb het gedaan"),
           "finish": dict(en="FINISH", de="FERTIG", it="FINITO", nl="KLAAR"),
           "right": dict(en="Just RIGHT", de="Genau RICHTIG", it="Così va bene", nl="Precies GOED"),
           "ignore": dict(en="IGNORE", de="IGNORIEREN", it="IGNORA", nl="Negeer"),
           "yes": dict(en="YES", de="JA", it="Sì ", nl="JA"),
           "no": dict(en="NO", de="NEIN", it="No", nl="Nee")}

weekDays = {"en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "de": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
            "it": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
            "nl": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
            }
ipaq = {
    "days_content": dict(en="Days per week:", de="Tage pro Woche:", it="Giorni alla settimana:", nl="Dagen per week:"),
    "minutes_content": dict(en="Minutes per day:", de="Minuten pro Tag:", it="Minuti al giorno:", nl="Minuten per dag"),
    "days": dict(en="Days per week:", de="Tage pro Woche:", it="Giorni alla settimana:", nl="Dagen per week:"),
    "minutes": dict(en="Minutes per day:", de="Minuten pro Tag:", it="Minuti al giorno:", nl="Minuten per dag")
}

mpam = {"enjoyment": dict(en="Because it is fun", de="Weil es Spaß macht", it="Perché è divertente",
                          nl="Omdat het leuk is"),
        "appearance": dict(en="To improve my appearance", de="Um besser auszusehen", it="Per migliorare il mio aspetto",
                           nl="Om mijn uiterlijk te verbeteren"),
        "social": dict(en="Because i want to be with my friends", de="Weil ich mit meinen Freunden zusammen sein will",
                       it="Perché voglio stare con i miei amici", nl="Omdat ik bij mijn vrienden wil zijn"),
        "fitness": dict(en="Because i want to have more energy", de="Weil ich mehr Energie haben will",
                        it="Perché voglio avere più energia", nl="Omdat ik meer energie wil hebben"),
        "competence": dict(en="Because i want to improve existing skills",
                           de="Weil ich vorhandene Fähigkeiten verbessern möchte",
                           it="Perché voglio migliorare le competenze esistenti",
                           nl="Omdat ik bestaande vaardigheden wil verbeteren"),
        "true": dict(en="strongly agree", de="stimme voll zu", it="fortemente d'accordo", nl="helemaal mee eens"),
        "false": dict(en="strongly disagree", de="stimme gar nicht zu", it="fortemente in disaccordo",
                      nl="helemaal mee oneens")
        }
activity_name = {"cycling": dict(en="Cycling", de="Radfahren", it="Ciclismo", nl="Fietsen"),
                 "walking": dict(en="Walking", de="Spazieren gehen", it="A passeggio", nl="wandelen"),
                 "shoveling": dict(en="Shoveling", de="Schneeschaufeln", it="Spalare la neve",
                                   nl="Om sneeuw te scheppen"),
                 "yoga": dict(en="Yoga", de="Yoga", it="Yoga", nl="Yoga"),
                 "strength": dict(en="Strength training", de="Krafttraining", it="Allenamento della forza",
                                  nl="Krachttraining")
                 }
and_name = dict(en="and", de="und", it="e", nl="en")

content_title = {"bullet point": dict(en="Tip", de="Tipp", it="Mancia", nl="Tip"),
                 "description": dict(en="Description", de="Beschreibung", it="Descrizione", nl="Omschrijving"),
                 "advantage": dict(en="Advantage", de="Vorteil", it="Vantaggio", nl="Voordeel"),
                 "warning": dict(en="Warning", de="Warnung", it="Avvertimento", nl="Waarschuwing"),
                 "contraindication": dict(en="Warning", de="Kontraindikation", it="Controindicazione",
                                          nl="Contra-indicatie")}

greetings = {"morning": dict(en="Good morning", de="Guten Morgen", it="Buongiorno", nl="Fietsen"),
             "afternoon": dict(en="Good afternoon", de="Guten Tag", it="Buon pomeriggio",
                                   nl="Goede dag"),
             "evening": dict(en="Good evening", de="Guten Abend", it="Buona serata", nl="Goedenavond")
                 }
title_goal_screen = {"weekly_credits": dict(en="Achieved: {} Credits\nAllocated: {} Credits\nGoal: {} Credits",
                                            de="Erreicht: {} Credits\nZugewiesen: {} Credits\nZiel: {} Credits",
                                            it="Raggiunti: {} Crediti\nAssegnati: {} Crediti\nObiettivo: {} Crediti",
                                            nl="Behaald: {} Credits\nToegewezen: {} Credits\nDoel: {} Credits"),
                     "new_week": dict(en="Welcome to a new week!", de="Willkommen in einer neuen Woche!",
                                      it="Benvenuto {benvenuta} in una nuova settimana!",
                                      nl="Welkom in een nieuwe week!"),
                     "allocate_credits": dict(en="Unassigned credits: ", de="Nicht vergebene Credits: ",
                                              it="Crediti non assegnati: ",
                                              nl="Niet-toegewezen kredieten: "),
                     "activity_missed": dict(
                         en="Missed activity: ",
                         de="Verpasste Aktivität: ",
                         it="Attività mancante:",
                         nl="Gemiste activiteit:"),
                     "activity_today_single": dict(
                         en="Your activity for today: ",
                         de="Deine heutige Aktivität: ",
                         it="La tua attività per oggi: ",
                         nl="Uw activiteit voor vandaag: "),
                     "activity_today_multiple": dict(
                         en="Your activities for today: ",
                         de="Deine heutigen Aktivitäten: ",
                         it="Le tue attività per oggi: ",
                         nl="Uw activiteiten voor vandaag: "),
                     "personal_week":dict(
                         en="Your week: {} till {}\nLeft days: {}",
                         de="Deine Woche: {} bis {}\nVerbleibende Tage: {}",
                         it="La tua settimana: dalle {} alle {}\nGiorni rimanenti: {}",
                         nl="Jouw week: {} tot {}\nResterende dagen: {}"),
                     }

text_to_speech = {"activity_today": dict(en="You have scheduled this activity for today. If you have it done already "
                                            "you can finish it by pressing the 'Activity Done' button.",
                                         de="Du hast diese Aktivität für heute geplant. Wenn du die Aktivität "
                                            "bereits getan hast, kannst du sie abschließen, indem du auf den Knopf "
                                            "'Aktivität abschließen' klickst.",
                                         it="Hai in programma questa attività per oggi. Se hai già fatto, "
                                            "puoi premere il pulsante 'Attività completata'.",
                                         nl="Je hebt deze activiteit voor vandaag gepland. Als je het al hebt gedaan, "
                                            "kun je dit aangeven door op de knop 'Activiteit voltooid' te drukken."),
                  "delete_info": dict(
                      en="You can delete all days on which you scheduled the activity without achieving it"
                         "by clicking on the 'Delete activity' button.",
                      de="Du kannst alle Tage an denen du die Aktivität eingetragen aber nicht "
                         "gemacht hast, löschen, indem du auf den Knopf 'Aktivität entfernen' klickst.",
                      it="Puoi eliminare tutti i giorni in cui hai pianificato l'attività senza completarla, "
                         "premendo il pulsante 'Elimina attività'.",
                      nl="U kunt alle dagen verwijderen waarop u de activiteit heeft gepland maar niet uitgevoerd "
                         "door op de knop 'Activiteit verwijderen' te drukken."),
                  "new_week": dict(
                      en="Hello{}! A new week just started which means you get new credits for the upcoming "
                         "7 days. Your old activities have been deleted, but you can watch your last weeks "
                         "performance on the goal information screen.",
                      de="Hallo{}! Eine neue Woche hat gerade begonnen, was bedeutet, dass du für die "
                         "kommenden 7 Tage neue Credits erhältst. Deine alten Aktivitäten wurden gelöscht "
                         "aber kein Sorge, du kannst deine Leistung der letzten Woche auf dem Info "
                         "Bildschirm nachsehen.",
                      it="Ciao{}! È appena iniziata una nuova settimana, il che significa che riceverai nuovi crediti "
                         "per i prossimi 7 giorni. Le tue vecchie attività sono state eliminate, ma puoi controllare "
                         "il rendimento delle ultime settimane nella schermata delle informazioni sull'obiettivo.",
                      nl="Hallo{}! Er is net een nieuwe week begonnen, wat betekent dat u nieuwe credits krijgt voor "
                         "de komende 7 dagen. Uw oude activiteiten zijn verwijderd, maar u kunt uw prestaties van de "
                         "afgelopen week bekijken op het scherm met het doelen overzicht."),
                  "allocate_mets_zero": dict(
                      en="Hello{}. I see you haven't allocated any credits for this week. Please do so in order "
                         "to stay active.",
                      de="Hallo{}. Wie ich sehe hast du noch keine Credits für diese Woche vergeben. Bitte "
                         "hole das das nach um weiterhin aktiv zu bleiben.",
                      it="Ciao{}. Vedo che non hai aggiunto crediti per questa settimana. Si prega di continuare a "
                         "farlo per rimanere in attività.",
                      nl="Hallo{}. Ik zie dat je deze week geen credits hebt toegewezen. Doe dit om actief te blijven."),
                  "allocate_mets": dict(
                      en="Hello{}.I see you haven't allocated all credits for this week. Please do so in order "
                         "to meet your wekkly goal and stay active.",
                      de="Hallo{}. Wie ich sehe hast du noch nicht alle Credits für diese Woche vergeben. Bitte "
                         "hole das nach um dein wöchentliches Ziel zu erreichen und weiterhin aktiv zu bleiben.",
                      it="Ciao{}. Vedo che non hai aggiunto tutti i crediti per questa settimana. Continua a farlo "
                         "per raggiungere il tuo obiettivo settimanale e non perdere l'allenamento.",
                      nl="Hallo{}. Ik zie dat je deze week niet alle credits hebt toegewezen. Doe dit om je "
                         "wekelijkse doel te bereiken en actief te blijven."),
                  "select_activity": dict(en="Please select a new physical activity for the upcoming week.",
                                          de="Bitte wähle eine eine neue Aktivität für die kommende Woche aus.",
                                          it="Seleziona un nuova attività fisica per la prossima settimana.",
                                          nl="Selecteer alstublieft een nieuwe beweegactiviteit voor de komende week."),
                  "days": dict(en="Please choose on which day(s) you want to exercise.",
                               de="Bitte wähle aus an welchen Tagen du die Aktivität machen möchtest.",
                               it="Scegli in quale giorno (i) desideri allenarti.",
                               nl="Kies alstublieft op welke dagen u de activiteiten wilt plannen."),
                  "days_edit": dict(en="Please choose which day(s) you want to add or remove.",
                                    de="Bitte wähle aus welche Tage du hinzufügen oder löschen möchtest.",
                                    it="Scegli il(i) giorno(i) che desideri aggiungere o rimuovere.",
                                    nl="Kies welke dagen u wilt toevoegen of verwijderen."),
                  "duration": dict(
                      en="Please choose a duration for your activity. You can see how the activity affects "
                         "your weekly goal on the bottom of the screen.",
                      de="Bitte wähle eine Dauer für deone Aktivität. Am unteren Bildschirmrand kannst "
                         "du sehen, wie sich die Aktivität auf dein wöchentliches Ziel auswirkt.",
                      it="Scegli la durata della tua attività. Nella parte inferiore dello schermo, puoi vedere "
                         "quanto l'attività influisce sul tuo obiettivo settimanale.",
                      nl="Kies de duur van uw activiteit. U kunt onderin het scherm zien hoe dit uw weekdoel beïnvloed."),
                  "goal_info": dict(en="Here are some details about your weekly performance.",
                                    de="Hier sind Details zu deiner wöchentlichen Leistung.",
                                    it="Ecco alcuni dettagli sulla tua perfomance settimanale.",
                                    nl="Hier zijn enkele details over uw wekelijkse behaalde doelen."),
                  "activity_today_single": dict(
                      en="Hey{}, I see you have an open activity for today. Plan your day accordingly so "
                         "you have enough time for it. When you have done it already you can finish "
                         "it by pressing the 'Activity Done' button on the activity screen.",
                      de="Hey{}, ich sehe, du hast heute eine offene Aktivität. Plane deinen Tag entsprechend, "
                         "damit du genug Zeit dafür hast. Wenn du die Aktivität bereits getan hast, kannst du sie "
                         "abschließen, indem du auf dem Aktivitätsbildschirm auf den Knopf 'Aktivität abschließen' klickst.",
                      it="Ehi {}, vedo che hai un'attività da svolgere oggi. Pianifica la tua giornata in modo da "
                         "avere abbastanza tempo per farlo. Quando avrai terminato, puoi premere il pulsante "
                         "'Attività completata' nella schermata dell'attività.",
                      nl="Hey {}, ik zie dat er voor vandaag een openstaande activiteit staat. Plan uw dag zodat u er "
                         "genoeg tijd voor heeft. Als u de activiteit al heeft uitgevoerd, kunt u dit aangeven door "
                         "op de knop 'Activiteit uitgevoerd' op het activiteitenscherm te drukken."),
                  "activity_today_multiple": dict(
                      en="Hey{}, I see you have open activities for today. Plan your day accordingly so "
                         "you have enough time for them. When you have done one of them already you can finish "
                         "it by pressing the 'Activity Done' button on the activity screen.",
                      de="Hey{}, ich sehe, du hast heute mehrere offene Aktivitäten. Plane deinen Tag entsprechend, "
                         "damit du genug Zeit für sie hast. Wenn du eine Aktivität bereits getan hast, kannst du sie "
                         "abschließen, indem du auf dem Aktivitätsbildschirm auf den Knopf 'Aktivität abschließen' klickst.",
                      it="Ehi {}, vedo che hai più attività da svolgere oggi. Pianifica la tua giornata in modo da "
                         "avere abbastanza tempo da dedicare ad esse. Quando ne hai già fatta una, puoi premere il "
                         "pulsante 'Attività completata' nella schermata dell'attività.",
                      nl="Hey {}, ik zie dat er voor vandaag openstaande activiteiten zijn. Plan uw dag zodat u er "
                         "genoeg tijd voor heeft. Als u er al een heeft uitgevoerd, kunt u dit aangeven door op de "
                         "knop 'Activiteit uitgevoerd' op het activiteitenscherm te drukken."),
                  "on_track": dict(
                      en="Hello there{}. Seems you have a break day today. Still, you can revise your weekly plan"
                         "or schedule an activity for today if you feel spontanous and fit. Otherwise "
                         "relax you need to be fit for the upcoming days",
                      de="Hallo{}. Ich sehe du hast heute einen Pausentag. Trotzdem kannst du deinen Wochenplan überarbeiten "
                         "oder eine Aktivität für heute planen wenn du spontan bist und dich fit fühlst. Andernfalls "
                         "entspanne dich, du musst ausgeruht für die kommenden Tage sein.",
                      it="Ciao{}. Sembra che tu abbia una giornata di pausa oggi. Puoi comunque rivedere il tuo "
                         "programma settimanale o programmare un'attività anche oggi se lo desideri e ti senti in "
                         "forma. Altrimenti rilassati, così sarai in forma per i prossimi giorni.",
                      nl="Hallo daar{}. Het lijkt erop dat u vandaag een rustdag hebt. Toch kunt u uw weekplan "
                         "herzien en een activiteit voor vandaag plannen als u zich fit voelt. U kunt ook uw energie "
                         "sparen voor de komende dagen."),
                  "activity_missed": dict(
                      en="Good to see you{}! I see you had tasks in the last days which you were not able to do. It is wise"
                         "to delete them in the activity screen to get credits back which you can use for new activities. That way you make"
                         "sure you meet your weekly goal.",
                      de="Schön dich zu sehen{}! Ich sehe, du hattest in den letzten Tagen geplante Aktivitäten, "
                         "die du nicht durchführen konntest. "
                         "Kein Problem, lösche diese Aktivitäten einfach im Aktivitätsbildschirm um Credits "
                         "zurückzugewinnen. Diese können "
                         "für neue Aktivitäten verwendet werden. Damit stellst du sicher, dass du dein  "
                         "wöchentliches Ziel erreichst.",
                      it="Piacere di rivederti{}!. Noto che negli ultimi giorni non sei riuscito {riuscita} a "
                         "svolgere alcune attività. Sarebbe meglio eliminarle dalla schermata per recuperare i "
                         "crediti che potrai utilizzare per nuove attività. Così ti assicuri di raggiungere il tuo "
                         "obiettivo settimanale.",
                      nl="Goed om u te zien{}!. Ik zie dat u de afgelopen dagen taken had die u niet kon doen. Het is "
                         "verstandig om ze te verwijderen in het activiteitenscherm, om credits terug te krijgen die "
                         "u kunt gebruiken voor nieuwe activiteiten. Op die manier zorgt u ervoor dat u uw wekelijkse "
                         "doel haalt."),
                  "activity_info": dict(
                      en="You can reschedule your days and duration for this activity by clicking the 'Edit Activity' "
                         "button.",
                      de="Du kannst die Tage und Dauer dieser Aktivität ändern wenn du auf den Knopf 'Aktivität "
                         "bearbeiten klickst.",
                      it="Puoi riprogrammare i giorni e la durata di questa attività facendo clic sul pulsante "
                         "'Modifica attività'.",
                      nl="U kunt de planning van de dagen en duur van activiteiten aanpassen door op de knop "
                         "'activiteiten aanpassen' te klikken"),

                  }
