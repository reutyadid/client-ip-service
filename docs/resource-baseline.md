# מדידת משאבים: kind, Traefik ו-ARC על Docker Desktop

> נמדד: 15.11.2026, בין 10:50 ל-11:05
> הרקע והשלבים מופיעים בסעיף 7 ב-`docs/work_plan.md`
> הקלאסטר היה זמני (`resource-test`), והוא נמחק בסוף המדידה

---

## 1. איך מדדנו

- בכל שלב חיכינו כ-60 שניות שהמערכת תתייצב. אחר כך לקחנו 3 דגימות, בהפרש של כ-20 שניות. בטבלה מופיע החציון.
- **זיכרון:** `free -b` בתוך WSL. ב-WSL2 כל ההפצות, וגם `docker-desktop`, רצות באותה מכונה וירטואלית. לכן `free` מראה את הזיכרון של כל ה-VM, כולל Docker.
- **מעבד:** אחוז ה-idle מ-`vmstat 5 2`, מהשורה השנייה, שהיא חלון של 5 שניות. בנוסף `kubectl top nodes`.
- **דיסק:** `docker system df`, `df -h /` ו-`Get-PSDrive C`. האימג'ים וה-volumes של Docker נשמרים בדיסק של `docker-desktop`, ולא ב-`/` של Ubuntu. לכן `df -h /` לא זז, והשינוי נראה בכונן C.
- הפלטים הגולמיים נשמרו בתיקייה הזמנית של הסשן (`scratchpad/resource-test/`).

## 2. גרסאות

| רכיב | גרסה |
|---|---|
| Docker Desktop (Engine) | 29.9.3 |
| kind | v0.33.0, אימג' הנוד `kindest/node:v1.37.0` |
| kubectl | v1.37.2 |
| helm | v4.3.1 |
| metrics-server chart | `metrics-server/metrics-server` 3.14.0, אפליקציה 0.9.0, עם `--kubelet-insecure-tls` |
| Traefik chart | `traefik/traefik` 42.4.0, אפליקציה v3.7.18, ערכי ברירת מחדל |
| ARC controller chart | `oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller` 0.15.1 |
| אימג' הרנר להשוואה | `ghcr.io/actions/actions-runner:2.338.2` |

**הסביבה:** Windows עם WSL2, ההפצות `Ubuntu-24.04` ו-`docker-desktop`. בקובץ `.wslconfig` מוגדר:

```ini
[wsl2]
memory=6GB
processors=4
swap=2GB
networkingMode=nat

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```

`nproc` מחזיר 4. `free` מראה סך הכול 5.8Gi זיכרון ו-2.0Gi swap.

**הכנה:** מחקנו את שלושת הקונטיינרים של `hello-counter`, ואת שתי הרשתות שלהם, שנשארו ריקות. האימג'ים וה-volumes נשארו. בקובץ ההגדרות של kind מיפינו את הפורטים 80 ו-443 של המחשב לפורטים 80 ו-443 של הנוד. שניהם היו פנויים.

## 3. תוצאות לפי שלב

| שלב | זיכרון בשימוש ב-WSL | זיכרון זמין ב-WSL | שינוי בזמין | CPU idle | צריכת הנוד (`docker stats`) | `kubectl top nodes` | פנוי בכונן C |
|---|---|---|---|---|---|---|---|
| בסיס, שום דבר לא רץ | 1,830 MiB | **4,096 MiB** (4.0 GiB) | – | 98% | – | – | 26.35 GB |
| + kind + metrics-server | 2,371 MiB | **3,555 MiB** (3.47 GiB) | −541 MiB | 90% | 910 MiB | 254m, 912Mi | 25.10 GB |
| + Traefik | 2,517 MiB | **3,409 MiB** (3.33 GiB) | −146 MiB | 89% | 1.04 GiB | 329m, 1063Mi | 24.92 GB |
| + ARC controller | 2,693 MiB | **3,234 MiB** (3.16 GiB) | −175 MiB | 91% | 1.27 GiB | 314m, 1293Mi | 24.74 GB |

**סיכום:** kind, Traefik והקונטרולר של ARC יחד צורכים בערך **860 MiB** מהזיכרון הזמין, ובערך 7–10% מעבד במנוחה. כ-0.3 ליבה מתוך 4.

**דיסק:** `df -h /` נשאר 5.5G בכל השלבים. ב-Docker נוסף volume של הנוד, שגדל מ-1.45GB אחרי הקמת kind ל-1.78GB אחרי ARC, ונמחק עם הקלאסטר. האימג' `kindest/node:v1.37.0` כבר היה במחשב.

## 4. מי צורך הכי הרבה בקלאסטר

חציון של `kubectl top pods -A` אחרי השלב האחרון, כש-kind, metrics-server, Traefik ו-ARC רצים:

| namespace | pod | CPU | זיכרון |
|---|---|---|---|
| kube-system | kube-apiserver | 91m | **464Mi** |
| kube-system | kube-controller-manager | 30m | 62Mi |
| kube-system | etcd | 51m | 58Mi |
| kube-system | kube-scheduler | 15m | 22Mi |
| traefik | traefik | 1m | 19Mi |
| kube-system | metrics-server | 5m | 18Mi |
| arc-systems | arc-gha-rs-controller | 2m | 14Mi |
| kube-system | coredns (×2) | 3m כל אחד | 12Mi כל אחד |
| kube-system | kube-proxy | 1m | 12Mi |
| kube-system | kindnet | 1m | 8Mi |
| local-path-storage | local-path-provisioner | 1m | 7Mi |

**תובנה:** Traefik ו-ARC עצמם קטנים מאוד, 19Mi ו-14Mi. רוב התוספת בשלבים 3 ו-4 הגיעה מ-`kube-apiserver`. הוא גדל מ-220Mi ל-305Mi אחרי Traefik, ול-464Mi אחרי ARC, כנראה בגלל ה-CRDs ששני הצ'ארטים מתקינים. ה-apiserver שומר אותם בזיכרון.

## 5. ה-listener והרנרים של ARC: לא נמדדו

אין עדיין טוקן או GitHub App, ולכן לא התקנו scale set. **נמדד רק הקונטרולר.** ה-listener ופודי הרנר לא נמדדו.

מה אומר התיעוד הרשמי של GitHub, בעמוד "Deploy runner scale sets":

- **listener:** פוד אחד לכל scale set, ב-namespace של הקונטרולר. בתיעוד אין ערכי ברירת מחדל או המלצת גודל. הדוגמה מגדירה requests ו-limits של `1` CPU ו-`1Gi` זיכרון, והיא מסומנת כדוגמה בלבד.
- **פוד רנר:** נוצר לכל ג'וב ונמחק בסופו. אם לא מגדירים `minRunners` ו-`maxRunners`, הוא יורד לאפס כשאין ג'ובים. הדוגמה בתיעוד מגדירה limits של `500m` CPU ו-`512Mi` זיכרון, גם היא כדוגמה בלבד. מומלץ להריץ את הרנרים ב-namespace נפרד מהקונטרולר.
- **`containerMode: dind`:** כל פוד רנר מקבל קונטיינר init, קונטיינר רנר וקונטיינר Docker-in-Docker, שחייב לרוץ ב-privileged. בפייפליין שלנו, שבונה אימג', זה הקונטיינר הכבד: הבנייה רצה בתוכו.
- **`dind-rootless`:** לפי התיעוד, ב-Ubuntu 24.04 ומעלה ההגבלות על user namespaces עלולות למנוע מ-RootlessKit להפעיל את ה-daemon.
- **`kubernetes` / `kubernetes-novolume`:** ג'ובים עם קונטיינר רצים בפוד נפרד דרך runner-container-hooks. אין צורך ב-privileged.

**המשמעות:** בזמן ג'וב, ה-listener, פוד הרנר ותהליך הבנייה והטסטים יתווספו לצריכה שנמדדה כאן.

## 6. השוואה: רנר בקונטיינר Docker (החלטה 10)

| מדד | ערך |
|---|---|
| אימג' | `ghcr.io/actions/actions-runner:2.338.2` |
| גודל האימג' בדיסק | **1.57 GB** |
| זיכרון במנוחה (`sleep 300` במקום ה-entrypoint, בלי רישום) | **2.6 MiB** |
| CPU במנוחה | 0.00% |

**הערה:** 2.6 MiB הם הצריכה של `sleep` בלבד. תהליך הרנר לא רץ, כי אין טוקן רישום. כשהרנר רשום ומחכה לג'וב, ייתכן שיצרוך עשרות MiB, אבל את זה לא מדדנו. ההבדל המרכזי בין הגישות הוא התשתית הקבועה: בגישת Docker אין קלאסטר שרץ כל הזמן בשביל הרנר. בגישת ARC הקונטרולר, ה-listener, ה-apiserver שגדל ו-etcd רצים כל הזמן. מצד שני, הפייפליין צריך kind בכל מקרה לשלב ה-deploy, ולכן התוספת של ARC עצמו מעל kind ו-Traefik נמדדה ב-175 MiB בלבד.

## 7. המלצה לפי כלל ההחלטה

**הכלל מסעיף 7:** אם אחרי kind, Traefik ו-ARC נשאר פחות מבערך 1.5 GiB זמין ב-WSL, נשארים עם קונטיינר Docker.

**התוצאה:** אחרי kind, Traefik והקונטרולר של ARC נשארו **3.16 GiB זמינים**, הרבה מעל הסף.

**ההמלצה:** לפי הכלל יש מקום לעבור ל-ARC בהמשך. **ההחלטה של רעות.** כמה דברים ששווה לשקול:

1. **המרווח בפועל קטן יותר:** ה-listener ופוד הרנר לא נמדדו. אם הרנר רץ ב-dind ובונה אימג' ומריץ טסטים, הבנייה בתוך הקלאסטר תצרוך כמה מאות MiB ויותר. כדאי למדוד שוב בזמן ג'וב אמיתי, אחרי שיהיה טוקן.
2. **הדיסק בכונן C הוא האילוץ הצפוף יותר:** נשארו בו בערך 22.6 GB אחרי המדידה. הוא ירד מ-26.35 GB בבסיס, בעיקר בגלל אימג' הרנר, 1.57 GB. כל אחת מהגישות מוסיפה אימג'ים ו-cache של בנייה. `docker system df` מראה כ-5.7GB של אימג'ים שאפשר לפנות, אבל לא פינינו אותם, וזו החלטה של רעות.
3. החלטה 10, קונטיינר Docker זמני, נשארת כמו שהיא. המדידה רק מראה שהמעבר ל-ARC אפשרי מבחינת זיכרון.

## 8. מגבלות המדידה

- **מדידה במנוחה בלבד.** לא רץ אף ג'וב, לא נבנה אימג' ולא עברה תעבורה דרך Traefik.
- **ARC חלקי:** נמדד רק הקונטרולר, בלי listener ובלי פודי רנר. פרטים בסעיף 5.
- **הרנר בקונטיינר נמדד עם `sleep`**, ולא כרנר רשום.
- **הזיכרון "הזמין" כולל cache.** `available` של `free` כולל buff/cache שהקרנל יכול לפנות, כ-3 GiB בזמן המדידה. עם `autoMemoryReclaim=gradual`, ה-VM מחזיר זיכרון ל-Windows בהדרגה, ולכן המספרים יכולים לזוז לאורך זמן.
- **קלאסטר טרי:** המדידה התחילה כ-2–5 דקות אחרי כל התקנה. ה-apiserver ו-etcd יכולים לגדול עוד לאורך זמן, ככל שנוספים אובייקטים.
- **דגימות מעטות:** 3 דגימות בכל שלב. אחוז ה-CPU של הנוד ב-`docker stats` קפץ בין 23% ל-63%, ולכן CPU idle ו-`kubectl top` אמינים יותר.
- לא נמדד הזיכרון בצד של Windows, מחוץ ל-VM.

## 9. Troubleshooting

לא הייתה תקלה שעצרה את המדידה. שתי הערות:

| תסמין | סיבה | פתרון |
|---|---|---|
| ה-Service של Traefik מסוג LoadBalancer נשאר עם `EXTERNAL-IP <pending>` | ב-kind אין cloud provider שמקצה כתובת חיצונית ל-LoadBalancer | לא היה צריך בשביל המדידה. בקלאסטר של הפרויקט אפשר להשתמש ב-NodePort או ב-hostPort, יחד עם ה-extraPortMappings של 80 ו-443, או להתקין cloud-provider-kind. |
| `docker pull` של `ghcr.io/actions/actions-runner` לקח יותר מ-3 דקות | האימג' גדול, 1.57 GB | לחכות. כדאי לקחת את זה בחשבון כשמשתמשים ברנר הזמני: האימג' נשאר במחשב, ולכן רק המשיכה הראשונה איטית. |

## 10. ניקוי

- `helm uninstall` ל-`arc`, ל-`traefik` ול-`metrics-server`
- `kind delete cluster --name resource-test`: הפקודה `kind get clusters` מחזירה "No kind clusters found", ו-`docker ps -a` ריק
- הקונטיינר `runner-idle-test` נמחק. האימג' `ghcr.io/actions/actions-runner:2.338.2` נשאר במחשב, 1.57 GB.
- helm נשאר מותקן. נוספו לו ה-repos `metrics-server` ו-`traefik`.
- אחרי הניקוי: 4.0Gi זמינים ב-WSL, כמו בבסיס, ו-22.59 GB פנויים בכונן C.
