"""
faq_service.py – Dynamic multilingual FAQ engine.

All FAQ answers use placeholder tokens like {university_name}, {portal_url},
{email_registrar}, etc. At search time these are replaced with real data
from the University object (or sensible defaults). This makes the FAQ
reusable for ANY Algerian university, not just Batna.
"""

import re
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Any


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """
    Detect whether the text is Arabic ('ar'), French ('fr'), or English ('en').
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    french_markers = len(re.findall(
        r'[àâçéèêëîïôùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŸŒÆ]', text
    ))
    french_words = len(re.findall(
        r'\b(je|tu|il|elle|nous|vous|ils|elles|le|la|les|un|une|des|du|de|et|est|'
        r'en|au|aux|avec|pour|sur|dans|par|que|qui|quoi|comment|quand|où|quel|quelle|'
        r'bonjour|salut|merci|oui|non|pourquoi|inscription|frais|cours|examens|'
        r'comment|puis|je|mon|ma|mes|ses)\b',
        text.lower()
    ))
    total_words = max(len(text.split()), 1)

    if arabic_chars > 1:
        return 'ar'
    if (french_markers + french_words) / total_words > 0.15 or french_words >= 2:
        return 'fr'
    return 'en'


# ---------------------------------------------------------------------------
# Placeholder builder
# ---------------------------------------------------------------------------

def build_placeholders(university=None) -> Dict[str, str]:
    """
    Build a dict of placeholder values from a University ORM object.
    Falls back to generic strings if no university is provided.
    """
    if university is None:
        return {
            'university_name':    'your university',
            'university_name_ar': 'جامعتك',
            'university_name_fr': 'votre université',
            'city':               'your city',
            'city_ar':            'مدينتك',
            'city_fr':            'votre ville',
            'portal_url':         'your student portal',
            'website':            'the university website',
            'email_general':      'info@university.dz',
            'email_registrar':    'registrar@university.dz',
            'email_finance':      'finance@university.dz',
            'email_it':           'itsupport@university.dz',
            'email_student':      'studentaffairs@university.dz',
            'email_financial_aid':'financialaid@university.dz',
            'email_housing':      'housing@university.dz',
            'email_library':      'library@university.dz',
            'email_academic':     'academic@university.dz',
            'phone_main':         'the university main number',
            'address':            'the university campus',
        }

    name    = university.name    or 'your university'
    name_ar = university.name_ar or 'جامعتك'
    city    = university.city    or ''
    website = university.website or 'the university website'
    email   = university.email   or 'info@university.dz'
    phone   = university.phone   or ''

    # Derive sub-emails from the domain of the main email
    domain = email.split('@')[-1] if '@' in email else 'university.dz'

    def sub(prefix):
        return f'{prefix}@{domain}'

    # Portal URL: prefer website, fall back to a generic label
    portal = website or 'the student portal'

    return {
        'university_name':     name,
        'university_name_ar':  name_ar,
        'university_name_fr':  name,           # French uses same Latin name
        'city':                city,
        'city_ar':             city,
        'city_fr':             city,
        'portal_url':          portal,
        'website':             website,
        'email_general':       email,
        'email_registrar':     sub('registrar'),
        'email_finance':       sub('finance'),
        'email_it':            sub('itsupport'),
        'email_student':       sub('studentaffairs'),
        'email_financial_aid': sub('financialaid'),
        'email_housing':       sub('housing'),
        'email_library':       sub('library'),
        'email_academic':      sub('academic'),
        'phone_main':          phone or 'the university main number',
        'address':             university.address or f'Campus of {name}, {city}',
    }


def fill(template: str, ph: Dict[str, str]) -> str:
    """Replace all {placeholder} tokens in template with actual values."""
    for key, val in ph.items():
        template = template.replace('{' + key + '}', val)
    return template


# ---------------------------------------------------------------------------
# FAQ database – fully generic (no Batna-specific data)
# ---------------------------------------------------------------------------

_FAQS: List[Dict[str, Any]] = [
    # 1. Greeting
    {
        "id": 1, "category": "greeting",
        "question": "Hello / Hi / Greetings",
        "answers": {
            "en": (
                "Hello! Welcome to {university_name} Chatbot. I'm here to help you with:\n"
                "- Course registration and enrollment\n"
                "- Tuition fees and payments\n"
                "- Academic information and grades\n"
                "- Campus facilities and services\n"
                "- Exams and schedules\n"
                "- Student services\n\n"
                "How can I assist you today?"
            ),
            "ar": (
                "مرحباً! أهلاً بك في شات بوت {university_name_ar}. أنا هنا لمساعدتك في:\n"
                "- التسجيل في المقررات\n"
                "- الرسوم الدراسية والمدفوعات\n"
                "- المعلومات الأكاديمية والدرجات\n"
                "- مرافق الحرم الجامعي والخدمات\n"
                "- الامتحانات والجداول الزمنية\n"
                "- خدمات الطلاب\n\n"
                "كيف يمكنني مساعدتك اليوم؟"
            ),
            "fr": (
                "Bonjour! Bienvenue sur le Chatbot de {university_name_fr}. Je suis là pour vous aider avec:\n"
                "- L'inscription aux cours\n"
                "- Les frais de scolarité et paiements\n"
                "- Les informations académiques et les notes\n"
                "- Les installations du campus et services\n"
                "- Les examens et les emplois du temps\n"
                "- Les services aux étudiants\n\n"
                "Comment puis-je vous aider aujourd'hui?"
            ),
        },
        "keywords": ["hello","hi","hey","greetings","salut","bonjour","salam",
                     "مرحبا","السلام عليكم","أهلا","هلا"],
        "variants": ["hello","hi there","hey","good morning","bonjour","salut","مرحبا","السلام عليكم"],
    },
    # 2. How are you
    {
        "id": 2, "category": "greeting",
        "question": "How are you?",
        "answers": {
            "en": "I'm functioning well, thank you! I'm ready to help you with any questions about {university_name}. What would you like to know?",
            "ar": "أنا بخير، شكراً لسؤالك! أنا جاهز لمساعدتك في أي سؤال يتعلق بـ{university_name_ar}. ماذا تريد أن تعرف؟",
            "fr": "Je fonctionne très bien, merci! Je suis prêt à vous aider pour toutes vos questions sur {university_name_fr}. Que souhaitez-vous savoir?",
        },
        "keywords": ["how are you","comment allez-vous","ça va","كيف حالك","كيفك","comment vas-tu"],
        "variants": ["how are you","how are you doing","comment vas-tu","كيف حالك"],
    },
    # 3. Thank you
    {
        "id": 3, "category": "greeting",
        "question": "Thank you / Thanks",
        "answers": {
            "en": "You're very welcome! I'm glad I could help. Feel free to ask anytime. Have a great day!",
            "ar": "على الرحب والسعة! يسعدني أنني استطعت المساعدة. لا تتردد في السؤال في أي وقت. أتمنى لك يوماً رائعاً!",
            "fr": "De rien! Je suis ravi d'avoir pu vous aider. N'hésitez pas à demander à tout moment. Bonne journée!",
        },
        "keywords": ["thank","thanks","merci","شكرا","شكراً","شكرًا"],
        "variants": ["thank you","thanks","merci","شكرا","شكراً جزيلاً"],
    },
    # 4. Goodbye
    {
        "id": 4, "category": "greeting",
        "question": "Goodbye / See you",
        "answers": {
            "en": "Goodbye! It was nice helping you today. Come back anytime you have questions about {university_name}. Take care!",
            "ar": "وداعاً! كان من دواعي سروري مساعدتك. عُد في أي وقت لديك أسئلة حول {university_name_ar}. اعتنِ بنفسك!",
            "fr": "Au revoir! C'était un plaisir de vous aider. Revenez à tout moment pour {university_name_fr}. Prenez soin de vous!",
        },
        "keywords": ["goodbye","bye","see you","au revoir","مع السلامة","وداعا"],
        "variants": ["goodbye","bye","see you later","au revoir","مع السلامة"],
    },
    # 5. What can you help with
    {
        "id": 5, "category": "help",
        "question": "What can you help me with?",
        "answers": {
            "en": (
                "I can help you with many aspects of {university_name}:\n\n"
                "📚 **Academic:** Course registration, grading system, attendance policies\n"
                "💰 **Financial:** Tuition fees, payment methods, scholarships\n"
                "🏢 **Campus Life:** Library, gym, cafeteria, student housing\n"
                "📝 **Student Services:** Student ID, portal access, admin procedures\n"
                "📅 **Important Dates:** Registration deadlines, exam periods\n\n"
                "Just ask me anything!"
            ),
            "ar": (
                "يمكنني مساعدتك في كثير من جوانب {university_name_ar}:\n\n"
                "📚 **الأكاديمي:** التسجيل في المقررات، نظام التقييم، سياسات الحضور\n"
                "💰 **المالي:** الرسوم الدراسية، طرق الدفع، المنح الدراسية\n"
                "🏢 **الحياة الجامعية:** المكتبة، قاعة الرياضة، المطعم، السكن الجامعي\n"
                "📝 **خدمات الطلاب:** بطاقة الطالب، الوصول إلى البوابة، الإجراءات الإدارية\n"
                "📅 **مواعيد هامة:** مواعيد التسجيل، فترات الامتحانات\n\n"
                "اسألني أي شيء!"
            ),
            "fr": (
                "Je peux vous aider avec de nombreux aspects de {university_name_fr}:\n\n"
                "📚 **Académique:** Inscription aux cours, système de notation, politiques de présence\n"
                "💰 **Financier:** Frais de scolarité, modes de paiement, bourses\n"
                "🏢 **Vie du campus:** Bibliothèque, gymnase, cafétéria, logement étudiant\n"
                "📝 **Services étudiants:** Carte étudiant, accès au portail, procédures administratives\n"
                "📅 **Dates importantes:** Dates d'inscription, périodes d'examens\n\n"
                "Posez-moi n'importe quelle question!"
            ),
        },
        "keywords": ["help","what can you do","aide","مساعدة","ماذا تفعل","ماذا تستطيع"],
        "variants": ["what can you help with","what do you do","how can you help","aide","مساعدة"],
    },
    # 6. Course registration
    {
        "id": 6, "category": "registration",
        "question": "How do I register for courses?",
        "answers": {
            "en": (
                "**Course Registration Process:**\n\n"
                "1. Log into the student portal: {portal_url}\n"
                "2. Navigate to 'Course Registration'\n"
                "3. Select your desired courses\n"
                "4. Check for time conflicts\n"
                "5. Submit your registration\n"
                "6. Pay registration fees within the deadline\n\n"
                "Registration opens 2 weeks before each semester. Limited seats – register early!\n\n"
                "📧 {email_registrar}"
            ),
            "ar": (
                "**خطوات التسجيل في المقررات:**\n\n"
                "1. سجّل الدخول على بوابة الطلاب: {portal_url}\n"
                "2. انتقل إلى قسم 'تسجيل المقررات'\n"
                "3. اختر المقررات المطلوبة\n"
                "4. تحقق من التعارض في الجداول\n"
                "5. أرسل طلب التسجيل\n"
                "6. ادفع رسوم التسجيل قبل الموعد النهائي\n\n"
                "يفتح التسجيل قبل أسبوعين من كل فصل. الأماكن محدودة – سجّل مبكراً!\n\n"
                "📧 {email_registrar}"
            ),
            "fr": (
                "**Processus d'inscription aux cours:**\n\n"
                "1. Connectez-vous au portail étudiant: {portal_url}\n"
                "2. Allez dans 'Inscription aux cours'\n"
                "3. Sélectionnez vos cours\n"
                "4. Vérifiez les conflits d'horaires\n"
                "5. Soumettez votre inscription\n"
                "6. Payez les frais dans le délai imparti\n\n"
                "L'inscription ouvre 2 semaines avant chaque semestre. Places limitées – inscrivez-vous tôt!\n\n"
                "📧 {email_registrar}"
            ),
        },
        "keywords": ["register","registration","enroll","enrollment","course","signup",
                     "inscription","inscrire","cours","تسجيل","مادة","كيف أسجل","كيف اسجل"],
        "variants": ["how to register","registration process","enroll in courses",
                     "comment s'inscrire","comment puis-je m inscrire","كيف أسجل","طريقة التسجيل"],
    },
    # 7. Registration deadlines
    {
        "id": 7, "category": "registration",
        "question": "What are the registration deadlines?",
        "answers": {
            "en": (
                "**Registration Deadlines:**\n\n"
                "🍂 Fall: Early registration → Regular → Late registration (with late fee)\n"
                "🌸 Spring: Early registration → Regular → Late registration (with late fee)\n"
                "☀️ Summer: Short registration window\n\n"
                "⚠️ Check the official academic calendar on {portal_url} for exact dates.\n"
                "Late registration incurs additional fees. No registration after late period ends!"
            ),
            "ar": (
                "**مواعيد التسجيل:**\n\n"
                "🍂 الخريف: تسجيل مبكر ← عادي ← متأخر (برسوم إضافية)\n"
                "🌸 الربيع: تسجيل مبكر ← عادي ← متأخر (برسوم إضافية)\n"
                "☀️ الصيف: فترة تسجيل قصيرة\n\n"
                "⚠️ راجع التقويم الأكاديمي الرسمي على {portal_url} للمواعيد الدقيقة.\n"
                "التسجيل المتأخر يستلزم رسوماً إضافية. لا يُقبل أي تسجيل بعد انتهاء الفترة!"
            ),
            "fr": (
                "**Dates limites d'inscription:**\n\n"
                "🍂 Automne: Inscription anticipée → Normale → Tardive (avec frais supplémentaires)\n"
                "🌸 Printemps: Inscription anticipée → Normale → Tardive (avec frais supplémentaires)\n"
                "☀️ Été: Courte période d'inscription\n\n"
                "⚠️ Consultez le calendrier académique officiel sur {portal_url} pour les dates exactes.\n"
                "L'inscription tardive entraîne des frais supplémentaires. Aucune inscription après la période tardive!"
            ),
        },
        "keywords": ["deadline","last day","registration date","when","due date",
                     "date limite","موعد","آخر موعد","متى التسجيل"],
        "variants": ["registration deadline","when to register","date limite d'inscription","موعد التسجيل"],
    },
    # 8. Drop a course
    {
        "id": 8, "category": "registration",
        "question": "Can I drop a course after registration?",
        "answers": {
            "en": (
                "**Course Drop Policy:**\n\n"
                "✅ Weeks 1-2 (Add/Drop Period): Full refund, no transcript record\n"
                "⚠️ Weeks 3-6 (Withdrawal): Partial refund, 'W' on transcript (no GPA impact)\n"
                "❌ After Week 6: No refund, 'WF' on transcript (affects GPA)\n\n"
                "How to Drop: via the student portal ({portal_url}) or the Registrar's Office.\n"
                "📧 {email_registrar}"
            ),
            "ar": (
                "**سياسة حذف المقررات:**\n\n"
                "✅ الأسبوعان 1-2: استرداد كامل، بدون سجل في كشف الدرجات\n"
                "⚠️ الأسابيع 3-6: استرداد جزئي، يظهر 'W' في كشف الدرجات (لا يؤثر على المعدل)\n"
                "❌ بعد الأسبوع 6: لا استرداد، يظهر 'WF' في كشف الدرجات (يؤثر على المعدل)\n\n"
                "طريقة الحذف: عبر بوابة الطالب ({portal_url}) أو مكتب التسجيل.\n"
                "📧 {email_registrar}"
            ),
            "fr": (
                "**Politique d'abandon de cours:**\n\n"
                "✅ Semaines 1-2: Remboursement total, aucune mention sur le relevé\n"
                "⚠️ Semaines 3-6: Remboursement partiel, 'W' sur le relevé (pas d'impact sur la moyenne)\n"
                "❌ Après la semaine 6: Pas de remboursement, 'WF' sur le relevé (affecte la moyenne)\n\n"
                "Comment abandonner: via le portail étudiant ({portal_url}) ou le Bureau du Registraire.\n"
                "📧 {email_registrar}"
            ),
        },
        "keywords": ["drop","withdraw","remove course","cancel registration","annuler",
                     "حذف المادة","الانسحاب","حذف مقرر"],
        "variants": ["drop a course","withdraw from course","annuler un cours","حذف مادة"],
    },
    # 9. Tuition fees
    {
        "id": 9, "category": "tuition",
        "question": "How much are the tuition fees?",
        "answers": {
            "en": (
                "**Tuition Fees (Per Semester):**\n\n"
                "🎓 Undergraduate: Base tuition + applicable lab fees\n"
                "🎓 Master's: Base tuition + research fees\n"
                "🎓 PhD: Base tuition + research & lab access fees\n\n"
                "Additional fees may include: registration, library access, sports facilities, and student services.\n\n"
                "💡 For exact amounts, check {portal_url} or contact the Finance Office: 📧 {email_finance}\n"
                "Scholarships are available – ask about financial aid!"
            ),
            "ar": (
                "**الرسوم الدراسية (لكل فصل):**\n\n"
                "🎓 الليسانس: رسوم أساسية + رسوم مختبر (إن وجدت)\n"
                "🎓 الماستر: رسوم أساسية + رسوم بحثية\n"
                "🎓 الدكتوراه: رسوم أساسية + رسوم مختبر وبحث\n\n"
                "قد تشمل الرسوم الإضافية: التسجيل، المكتبة، الرياضة، والخدمات الطلابية.\n\n"
                "💡 للمبالغ الدقيقة، راجع {portal_url} أو تواصل مع الشؤون المالية: 📧 {email_finance}\n"
                "تتوفر منح دراسية – اسأل عن المساعدات المالية!"
            ),
            "fr": (
                "**Frais de scolarité (par semestre):**\n\n"
                "🎓 Licence: Frais de base + frais de laboratoire (si applicable)\n"
                "🎓 Master: Frais de base + frais de recherche\n"
                "🎓 Doctorat: Frais de base + accès labo et recherche\n\n"
                "Des frais supplémentaires peuvent inclure: inscription, bibliothèque, sports, et services étudiants.\n\n"
                "💡 Pour les montants exacts, consultez {portal_url} ou contactez le Bureau des finances: 📧 {email_finance}\n"
                "Des bourses sont disponibles – renseignez-vous sur l'aide financière!"
            ),
        },
        "keywords": ["tuition","fees","cost","price","how much","money",
                     "frais","scolarite","scolarité",
                     "رسوم","المصاريف","كم الرسوم","كم التكلفة","الرسوم الدراسية","ما هي الرسوم"],
        "variants": ["tuition fees","how much does it cost","frais de scolarité",
                     "quels sont les frais","كم الرسوم","الرسوم الدراسية"],
    },
    # 10. Payment methods
    {
        "id": 10, "category": "tuition",
        "question": "What payment methods are accepted?",
        "answers": {
            "en": (
                "**Accepted Payment Methods:**\n\n"
                "🏦 Bank Transfer: to the university's official bank account (reference: your Student ID)\n"
                "💵 Cash: at the Finance Office on campus (office hours: Sun–Thu 8AM–4PM)\n"
                "📮 Postal account (CCP) if available\n"
                "💳 Online payment via {portal_url}/payment (CIB, EDAHABIA, Visa, Mastercard)\n\n"
                "📧 Always send your payment receipt to: {email_finance}\n"
                "☎ Finance Office: {phone_main}"
            ),
            "ar": (
                "**طرق الدفع المقبولة:**\n\n"
                "🏦 تحويل بنكي: إلى الحساب الرسمي للجامعة (المرجع: رقم الطالب)\n"
                "💵 نقداً: في مكتب الشؤون المالية بالحرم الجامعي (أوقات العمل: الأحد–الخميس 8ص–4م)\n"
                "📮 حساب بريدي (CCP) إن كان متاحاً\n"
                "💳 دفع إلكتروني عبر {portal_url}/payment (CIB، EDAHABIA، Visa، Mastercard)\n\n"
                "📧 أرسل دائماً إيصال الدفع إلى: {email_finance}\n"
                "☎ الشؤون المالية: {phone_main}"
            ),
            "fr": (
                "**Modes de paiement acceptés:**\n\n"
                "🏦 Virement bancaire: sur le compte officiel de l'université (réf: votre ID étudiant)\n"
                "💵 Espèces: au Bureau des finances sur le campus (Dim–Jeu 8h–16h)\n"
                "📮 Compte postal (CCP) si disponible\n"
                "💳 Paiement en ligne via {portal_url}/payment (CIB, EDAHABIA, Visa, Mastercard)\n\n"
                "📧 Envoyez toujours votre reçu à: {email_finance}\n"
                "☎ Bureau des finances: {phone_main}"
            ),
        },
        "keywords": ["payment","pay","method","transfer","cash","online","credit card",
                     "paiement","طريقة الدفع","كيف أدفع","دفع"],
        "variants": ["how to pay","payment methods","modes de paiement","كيف أدفع"],
    },
    # 11. Grading system
    {
        "id": 11, "category": "academic",
        "question": "What is the grading system?",
        "answers": {
            "en": (
                "**Algerian Grading Scale (0-20):**\n\n"
                "- 16-20: Excellent (Très Bien) → A\n"
                "- 14-15.99: Very Good (Bien) → B\n"
                "- 12-13.99: Good (Assez Bien) → C\n"
                "- 10-11.99: Satisfactory (Passable) → D\n"
                "- Below 10: Fail (Ajourné) → F\n\n"
                "**Minimum passing grade:** 10/20\n\n"
                "**Typical grade components:** Midterm ~30% | Final ~50% | Assignments ~15% | Attendance ~5%\n\n"
                "Grade appeals: usually within 5 days of grade publication. Contact {email_academic} for details."
            ),
            "ar": (
                "**سلم التقييم الجزائري (0-20):**\n\n"
                "- 16-20: ممتاز (Très Bien) → A\n"
                "- 14-15.99: جيد جداً (Bien) → B\n"
                "- 12-13.99: جيد (Assez Bien) → C\n"
                "- 10-11.99: مقبول (Passable) → D\n"
                "- أقل من 10: راسب (Ajourné) → F\n\n"
                "**الحد الأدنى للنجاح:** 10/20\n\n"
                "**مكونات الدرجة المعتادة:** منتصف الفصل ~30% | نهائي ~50% | واجبات ~15% | حضور ~5%\n\n"
                "التظلم على الدرجات: عادةً خلال 5 أيام من النشر. تواصل مع {email_academic} للتفاصيل."
            ),
            "fr": (
                "**Barème de notation algérien (0-20):**\n\n"
                "- 16-20: Excellent (Très Bien) → A\n"
                "- 14-15.99: Très Bien (Bien) → B\n"
                "- 12-13.99: Bien (Assez Bien) → C\n"
                "- 10-11.99: Passable → D\n"
                "- Moins de 10: Ajourné (Échec) → F\n\n"
                "**Note minimale pour réussir:** 10/20\n\n"
                "**Répartition habituelle:** Partiel ~30% | Final ~50% | Devoirs ~15% | Présence ~5%\n\n"
                "Recours: généralement dans les 5 jours après la publication. Contactez {email_academic}."
            ),
        },
        "keywords": ["grade","grading","marks","score","gpa","evaluation","notation",
                     "درجات","تقييم","نظام الدرجات","النقطة"],
        "variants": ["grading system","how grades work","système de notation","نظام التقييم"],
    },
    # 12. Check grades
    {
        "id": 12, "category": "academic",
        "question": "How can I access my grades?",
        "answers": {
            "en": (
                "**Accessing Your Grades:**\n\n"
                "💻 Online: {portal_url} → Academic Records → View Grades\n"
                "📧 You'll receive an email notification when grades are posted\n"
                "🏢 In person: Registrar's Office (Student ID required) – fee for official sealed copy\n\n"
                "Grades are typically posted within 1-2 weeks after exams.\n"
                "📧 IT issues: {email_it}"
            ),
            "ar": (
                "**طريقة الاطلاع على الدرجات:**\n\n"
                "💻 إلكترونياً: {portal_url} ← السجلات الأكاديمية ← عرض الدرجات\n"
                "📧 ستتلقى إشعاراً بالبريد الإلكتروني عند نشر الدرجات\n"
                "🏢 حضورياً: مكتب التسجيل (بطاقة الطالب مطلوبة) – رسوم للنسخة الرسمية المختومة\n\n"
                "تُنشر الدرجات عادةً خلال 1-2 أسبوع بعد الامتحانات.\n"
                "📧 مشاكل تقنية: {email_it}"
            ),
            "fr": (
                "**Accéder à vos notes:**\n\n"
                "💻 En ligne: {portal_url} → Dossier académique → Voir les notes\n"
                "📧 Vous recevrez un email de notification quand les notes sont disponibles\n"
                "🏢 En personne: Bureau du Registraire (carte étudiant requise) – frais pour copie officielle\n\n"
                "Les notes sont généralement publiées dans les 1-2 semaines après les examens.\n"
                "📧 Problèmes techniques: {email_it}"
            ),
        },
        "keywords": ["access grades","view grades","check grades","see results","transcript",
                     "consulter notes","الاطلاع على النتائج","أشوف درجاتي","كيف أرى نتائجي"],
        "variants": ["how to see grades","check my grades","voir mes notes","كيف أرى درجاتي"],
    },
    # 13. Attendance
    {
        "id": 13, "category": "academic",
        "question": "What is the attendance policy?",
        "answers": {
            "en": (
                "**Attendance Policy (Algerian universities):**\n\n"
                "✅ Minimum required attendance: 75% per course\n"
                "- First few absences: tolerated\n"
                "- Further absences: warning, then grade deductions\n"
                "- Exceeding 25% absence rate: Automatic failure\n\n"
                "Excused absences (medical certificate or official document) must be submitted within 3 days.\n"
                "Typically, 3 late arrivals (>15 min) count as 1 absence.\n\n"
                "📧 Contact {email_student} for absence justification procedures."
            ),
            "ar": (
                "**سياسة الحضور (الجامعات الجزائرية):**\n\n"
                "✅ الحد الأدنى المطلوب: 75% لكل مقرر\n"
                "- الغيابات الأولى: متسامح بها\n"
                "- الغيابات الإضافية: تحذير ثم خصم من الدرجة\n"
                "- تجاوز 25% من الغيابات: رسوب تلقائي\n\n"
                "الغياب المبرر (شهادة طبية أو وثيقة رسمية) يجب تقديمه خلال 3 أيام.\n"
                "عادةً 3 تأخيرات (>15 دقيقة) = غياب واحد.\n\n"
                "📧 تواصل مع {email_student} لإجراءات تبرير الغياب."
            ),
            "fr": (
                "**Politique de présence (universités algériennes):**\n\n"
                "✅ Présence minimale requise: 75% par cours\n"
                "- Premières absences: tolérées\n"
                "- Absences supplémentaires: avertissement puis déduction de points\n"
                "- Dépasser 25% d'absences: Échec automatique\n\n"
                "Absences justifiées (certificat médical ou document officiel) à soumettre dans les 3 jours.\n"
                "En général, 3 retards (>15 min) = 1 absence.\n\n"
                "📧 Contactez {email_student} pour les procédures de justification d'absence."
            ),
        },
        "keywords": ["attendance","absence","present","miss class","skip",
                     "assiduité","présence","الحضور","الغياب","غياب"],
        "variants": ["attendance policy","missing class","politique de présence","سياسة الحضور"],
    },
    # 14. Campus facilities
    {
        "id": 14, "category": "campus",
        "question": "What facilities are available on campus?",
        "answers": {
            "en": (
                "**Campus Facilities at {university_name}:**\n\n"
                "📚 Central Library: books, journals, e-resources, study rooms, free WiFi\n"
                "💻 Computer Labs: high-speed internet, software for all majors\n"
                "🏃 Sports Complex: gym, sports fields and courts\n"
                "🍽️ Student Cafeteria: subsidized meals\n"
                "🏥 Medical Clinic: basic healthcare, first aid\n"
                "🖨️ Printing Center: B&W and color printing\n"
                "🚗 Student parking (free with ID)\n\n"
                "For details and opening hours, visit {portal_url} or check the campus map at reception."
            ),
            "ar": (
                "**مرافق الحرم الجامعي في {university_name_ar}:**\n\n"
                "📚 المكتبة المركزية: كتب، دوريات، موارد إلكترونية، قاعات دراسة، واي فاي مجاني\n"
                "💻 قاعات الكمبيوتر: إنترنت عالي السرعة، برامج لجميع التخصصات\n"
                "🏃 المجمع الرياضي: صالة رياضة، ملاعب رياضية\n"
                "🍽️ المطعم الجامعي: وجبات مدعومة\n"
                "🏥 العيادة الطبية: رعاية صحية أساسية، إسعافات أولية\n"
                "🖨️ مركز الطباعة: طباعة بالأبيض والأسود وملونة\n"
                "🚗 موقف سيارات مجاني ببطاقة الطالب\n\n"
                "للتفاصيل وأوقات العمل، زر {portal_url} أو تحقق من خريطة الحرم الجامعي."
            ),
            "fr": (
                "**Équipements du campus de {university_name_fr}:**\n\n"
                "📚 Bibliothèque centrale: livres, revues, ressources numériques, salles d'étude, WiFi gratuit\n"
                "💻 Salles informatiques: internet haut débit, logiciels pour toutes les filières\n"
                "🏃 Complexe sportif: salle de gym, terrains de sport\n"
                "🍽️ Cafétéria étudiante: repas subventionnés\n"
                "🏥 Clinique médicale: soins de base, premiers secours\n"
                "🖨️ Centre d'impression: impression N&B et couleur\n"
                "🚗 Parking étudiant gratuit avec carte\n\n"
                "Pour les détails et horaires, consultez {portal_url} ou le plan du campus à la réception."
            ),
        },
        "keywords": ["facilities","campus","library","gym","cafeteria","sports",
                     "مرافق","مكتبة","ملعب","مطعم"],
        "variants": ["campus facilities","what's on campus","installations du campus","مرافق الجامعة"],
    },
    # 15. Library hours
    {
        "id": 15, "category": "campus",
        "question": "What are the library hours?",
        "answers": {
            "en": (
                "**Library Hours:**\n\n"
                "📅 Regular semester: Sun–Thu 8AM–8PM | Fri 8AM–12PM & 2PM–6PM | Sat 8AM–2PM\n"
                "📚 Exam period: extended hours (often until 10PM)\n"
                "🌙 Closed: national holidays; reduced hours during Ramadan\n"
                "💻 Digital library: 24/7 via {portal_url}\n\n"
                "📧 Library inquiries: {email_library}"
            ),
            "ar": (
                "**أوقات عمل المكتبة:**\n\n"
                "📅 الفصل الدراسي: الأحد–الخميس 8ص–8م | الجمعة 8ص–12م و2م–6م | السبت 8ص–2م\n"
                "📚 فترة الامتحانات: ساعات ممتدة (غالباً حتى 10م)\n"
                "🌙 مغلق: في العطل الوطنية؛ ساعات مختصرة خلال رمضان\n"
                "💻 المكتبة الرقمية: 24/7 عبر {portal_url}\n\n"
                "📧 استفسارات المكتبة: {email_library}"
            ),
            "fr": (
                "**Horaires de la bibliothèque:**\n\n"
                "📅 Semestre normal: Dim–Jeu 8h–20h | Ven 8h–12h & 14h–18h | Sam 8h–14h\n"
                "📚 Période d'examens: horaires étendus (souvent jusqu'à 22h)\n"
                "🌙 Fermée: jours fériés; horaires réduits pendant le Ramadan\n"
                "💻 Bibliothèque numérique: 24h/24 via {portal_url}\n\n"
                "📧 Renseignements bibliothèque: {email_library}"
            ),
        },
        "keywords": ["library","hours","time","open","close","schedule",
                     "horaires","bibliothèque","ساعات المكتبة","مكتبة"],
        "variants": ["library hours","when is library open","horaires de la bibliothèque","أوقات المكتبة"],
    },
    # 16. Student ID
    {
        "id": 16, "category": "services",
        "question": "How do I get a student ID card?",
        "answers": {
            "en": (
                "**Student ID Card:**\n\n"
                "📋 Typically required: passport-size photo, registration confirmation, national ID, payment of card fee\n"
                "🏢 Apply at: the Student Services Office on campus\n"
                "⏰ Processing time: usually 3-7 business days\n\n"
                "Lost card? Report immediately to the Student Services Office to get a replacement.\n"
                "⚠️ Your student ID is mandatory for exams, library access, and campus facilities!\n\n"
                "📧 {email_student}"
            ),
            "ar": (
                "**بطاقة الطالب:**\n\n"
                "📋 المطلوب عادةً: صورة شخصية، تأكيد التسجيل، بطاقة الهوية الوطنية، دفع رسوم البطاقة\n"
                "🏢 التقديم في: مكتب خدمات الطلاب بالحرم الجامعي\n"
                "⏰ مدة الإنجاز: عادةً 3-7 أيام عمل\n\n"
                "فقدت بطاقتك؟ أبلغ فوراً مكتب خدمات الطلاب للحصول على بدل ضائع.\n"
                "⚠️ بطاقة الطالب إلزامية للامتحانات والمكتبة ومرافق الجامعة!\n\n"
                "📧 {email_student}"
            ),
            "fr": (
                "**Carte étudiant:**\n\n"
                "📋 Généralement requis: photo d'identité, confirmation d'inscription, pièce d'identité nationale, paiement des frais de carte\n"
                "🏢 Demande à: le Bureau des services étudiants sur le campus\n"
                "⏰ Délai: généralement 3-7 jours ouvrables\n\n"
                "Carte perdue? Signalez immédiatement au Bureau des services étudiants pour obtenir un remplacement.\n"
                "⚠️ Votre carte étudiant est obligatoire pour les examens, la bibliothèque et les installations!\n\n"
                "📧 {email_student}"
            ),
        },
        "keywords": ["student id","card","identification","badge",
                     "carte étudiant","بطاقة الطالب","بطاقة طالب"],
        "variants": ["get student card","student id card","obtenir carte étudiant","الحصول على بطاقة الطالب"],
    },
    # 17. Housing
    {
        "id": 17, "category": "services",
        "question": "Is there student housing available?",
        "answers": {
            "en": (
                "**Student Housing:**\n\n"
                "🏠 On-campus dormitories (résidence universitaire) are available at most Algerian universities.\n"
                "💰 Monthly fees vary by room type (shared or single).\n"
                "📋 Priority is typically given to: students from distant regions, international students, and scholarship recipients.\n\n"
                "**How to apply:** Submit your application via {portal_url} during the housing application period (usually before the start of each semester).\n\n"
                "📧 Housing inquiries: {email_housing}"
            ),
            "ar": (
                "**السكن الجامعي:**\n\n"
                "🏠 تتوفر مساكن جامعية (إقامة جامعية) في معظم الجامعات الجزائرية.\n"
                "💰 الرسوم الشهرية تختلف حسب نوع الغرفة (مشتركة أو فردية).\n"
                "📋 الأولوية عادةً لـ: الطلاب القادمين من مناطق بعيدة، الطلاب الأجانب، والمنتفعين بالمنح.\n\n"
                "**طريقة التقديم:** قدّم طلبك عبر {portal_url} خلال فترة التقديم للسكن (عادةً قبل بداية كل فصل).\n\n"
                "📧 استفسارات السكن: {email_housing}"
            ),
            "fr": (
                "**Logement étudiant:**\n\n"
                "🏠 Des résidences universitaires sont disponibles dans la plupart des universités algériennes.\n"
                "💰 Les frais mensuels varient selon le type de chambre (partagée ou individuelle).\n"
                "📋 La priorité est généralement accordée aux: étudiants de régions éloignées, étudiants internationaux, et boursiers.\n\n"
                "**Comment postuler:** Soumettez votre candidature via {portal_url} pendant la période de demande de logement (généralement avant le début de chaque semestre).\n\n"
                "📧 Renseignements logement: {email_housing}"
            ),
        },
        "keywords": ["housing","dormitory","residence","accommodation","room","dorm",
                     "logement","résidence","السكن الجامعي","إقامة"],
        "variants": ["student housing","dormitories","résidence universitaire","السكن الجامعي"],
    },
    # 18. Scholarships
    {
        "id": 18, "category": "financial_aid",
        "question": "What scholarships are available?",
        "answers": {
            "en": (
                "**Scholarship Opportunities:**\n\n"
                "🏆 Merit-based: for students with high academic performance\n"
                "💰 Need-based: financial aid based on family income\n"
                "🔬 Research scholarships: for Master's and PhD students (includes tuition waiver + stipend)\n"
                "⚽ Sports scholarships: for university team members\n"
                "🌍 International student scholarships: tuition support for non-Algerian students\n\n"
                "📋 Applications are submitted via {portal_url} or at the Financial Aid Office.\n"
                "📧 {email_financial_aid}"
            ),
            "ar": (
                "**المنح الدراسية المتاحة:**\n\n"
                "🏆 منحة التميز: للطلاب ذوي الأداء الأكاديمي المرتفع\n"
                "💰 المنحة الاجتماعية: دعم مالي بناءً على دخل الأسرة\n"
                "🔬 منح البحث: لطلاب الماستر والدكتوراه (إعفاء من الرسوم + مخصص مالي)\n"
                "⚽ منح الرياضة: لأعضاء الفرق الجامعية\n"
                "🌍 منح الطلاب الأجانب: دعم الرسوم لغير الجزائريين\n\n"
                "📋 تُقدَّم الطلبات عبر {portal_url} أو في مكتب المنح الدراسية.\n"
                "📧 {email_financial_aid}"
            ),
            "fr": (
                "**Bourses disponibles:**\n\n"
                "🏆 Bourses au mérite: pour les étudiants avec d'excellents résultats académiques\n"
                "💰 Aide financière: soutien basé sur les revenus familiaux\n"
                "🔬 Bourses de recherche: pour les étudiants en Master et Doctorat (exonération + bourse mensuelle)\n"
                "⚽ Bourses sportives: pour les membres des équipes universitaires\n"
                "🌍 Bourses étudiants internationaux: aide pour les non-Algériens\n\n"
                "📋 Les candidatures se font via {portal_url} ou au Bureau des bourses.\n"
                "📧 {email_financial_aid}"
            ),
        },
        "keywords": ["scholarship","financial aid","funding","grant","support",
                     "bourse","aide financière","منحة","دعم مالي"],
        "variants": ["scholarships available","financial help","bourses disponibles","المنح الدراسية"],
    },
    # 19. Password reset
    {
        "id": 19, "category": "technical",
        "question": "I forgot my student portal password. How do I reset it?",
        "answers": {
            "en": (
                "**Password Reset:**\n\n"
                "💻 Online self-reset:\n"
                "   1. Go to {portal_url}\n"
                "   2. Click 'Forgot Password?'\n"
                "   3. Enter your university email address\n"
                "   4. Check your inbox (and spam folder!) for the reset link\n"
                "   5. Click the link (usually valid for 24h) and set a new password\n\n"
                "🏢 In person: visit the IT Support Office on campus with your Student ID + National ID\n\n"
                "📧 IT Support: {email_it}\n"
                "⚠️ The university will NEVER ask for your password by email."
            ),
            "ar": (
                "**إعادة تعيين كلمة المرور:**\n\n"
                "💻 إعادة تعيين إلكترونية:\n"
                "   1. اذهب إلى {portal_url}\n"
                "   2. انقر على 'نسيت كلمة المرور؟'\n"
                "   3. أدخل بريدك الجامعي\n"
                "   4. تحقق من صندوق الوارد (وبريد السبام!) للرابط\n"
                "   5. انقر الرابط (صالح عادةً 24 ساعة) وعيّن كلمة مرور جديدة\n\n"
                "🏢 حضورياً: زر مكتب الدعم التقني بالحرم الجامعي مع بطاقة الطالب + بطاقة الهوية\n\n"
                "📧 الدعم التقني: {email_it}\n"
                "⚠️ لن تطلب الجامعة منك كلمة المرور عبر البريد الإلكتروني أبداً."
            ),
            "fr": (
                "**Réinitialisation du mot de passe:**\n\n"
                "💻 Réinitialisation en ligne:\n"
                "   1. Allez sur {portal_url}\n"
                "   2. Cliquez sur 'Mot de passe oublié?'\n"
                "   3. Entrez votre email universitaire\n"
                "   4. Vérifiez votre boîte (y compris les spams!) pour le lien\n"
                "   5. Cliquez le lien (valide généralement 24h) et créez un nouveau mot de passe\n\n"
                "🏢 En personne: rendez-vous au Bureau IT du campus avec carte étudiant + pièce d'identité\n\n"
                "📧 Support IT: {email_it}\n"
                "⚠️ L'université ne vous demandera JAMAIS votre mot de passe par email."
            ),
        },
        "keywords": ["password","reset","forgot","login","access","portal",
                     "mot de passe","oublié","oublie","reinitialiser","réinitialiser",
                     "كلمة السر","نسيت","نسيت كلمة المرور","كلمة المرور"],
        "variants": ["reset password","forgot password","réinitialiser mot de passe",
                     "j ai oublié mot de passe","mot de passe oublié","نسيت كلمة السر"],
    },
    # 20. Exam schedule
    {
        "id": 20, "category": "exams",
        "question": "When are the exam periods?",
        "answers": {
            "en": (
                "**Exam Periods (typical Algerian academic calendar):**\n\n"
                "🍂 Fall Semester: Midterm exams (November) | Final exams (January) | Makeup/Resit (February)\n"
                "🌸 Spring Semester: Midterm exams (April) | Final exams (June) | Makeup/Resit (July)\n"
                "☀️ Summer session: Final exams (August/September)\n\n"
                "📅 Official exam schedules are posted 2-3 weeks before exams on {portal_url}.\n"
                "Results are published within 1-2 weeks after exams.\n"
                "📧 Academic affairs: {email_academic}"
            ),
            "ar": (
                "**فترات الامتحانات (التقويم الأكاديمي الجزائري المعتاد):**\n\n"
                "🍂 الفصل الخريفي: اختبارات منتصف الفصل (نوفمبر) | نهائي (يناير) | استدراكي (فبراير)\n"
                "🌸 الفصل الربيعي: اختبارات منتصف الفصل (أبريل) | نهائي (يونيو) | استدراكي (يوليو)\n"
                "☀️ الدورة الصيفية: نهائي (أغسطس/سبتمبر)\n\n"
                "📅 تُنشر جداول الامتحانات الرسمية قبل 2-3 أسابيع على {portal_url}.\n"
                "تُعلن النتائج خلال 1-2 أسبوع بعد الامتحانات.\n"
                "📧 الشؤون الأكاديمية: {email_academic}"
            ),
            "fr": (
                "**Périodes d'examens (calendrier académique algérien type):**\n\n"
                "🍂 Semestre d'automne: Partiels (novembre) | Examens finals (janvier) | Rattrapages (février)\n"
                "🌸 Semestre de printemps: Partiels (avril) | Examens finals (juin) | Rattrapages (juillet)\n"
                "☀️ Session d'été: Examens finals (août/septembre)\n\n"
                "📅 Les emplois du temps officiels sont publiés 2-3 semaines avant les examens sur {portal_url}.\n"
                "Les résultats sont publiés dans les 1-2 semaines suivant les examens.\n"
                "📧 Affaires académiques: {email_academic}"
            ),
        },
        "keywords": ["exam","test","final","schedule","when","period",
                     "examen","examens","quand","date",
                     "امتحان","الاختبار","موعد الامتحان","امتحانات","متى الامتحان",
                     "جدول الامتحانات"],
        "variants": ["exam schedule","when are exams","calendrier des examens",
                     "quand sont les examens","مواعيد الامتحانات","متى الامتحانات"],
    },
    # 21. Exam checklist
    {
        "id": 21, "category": "exams",
        "question": "What should I bring to exams?",
        "answers": {
            "en": (
                "**Exam Checklist:**\n\n"
                "✅ Required: Student ID (no ID = no entry!), blue/black pens, pencils, eraser\n"
                "✅ If allowed by instructor: non-programmable calculator, ruler\n"
                "✅ Recommended: clear water bottle, extra pens, watch\n\n"
                "❌ Strictly prohibited: mobile phones, smart watches, notes/books (unless open-book),\n"
                "   programmable calculators, earphones, any communication device\n\n"
                "Arrive at least 15 minutes early.\n"
                "Entry is typically denied if you arrive more than 15 minutes late.\n"
                "Good luck! 🍀"
            ),
            "ar": (
                "**قائمة مستلزمات الامتحان:**\n\n"
                "✅ إلزامي: بطاقة الطالب (بدون بطاقة = لا دخول!)، أقلام حبر أزرق/أسود، أقلام رصاص، ممحاة\n"
                "✅ إذا أجاز الأستاذ: آلة حاسبة غير قابلة للبرمجة، مسطرة\n"
                "✅ موصى به: زجاجة ماء شفافة، أقلام احتياطية، ساعة\n\n"
                "❌ محظور تماماً: الهاتف المحمول، الساعة الذكية، الأوراق والكتب (إلا إذا كان الامتحان مفتوحاً),\n"
                "   الآلات الحاسبة القابلة للبرمجة، سماعات الأذن، أي جهاز تواصل\n\n"
                "احضر قبل 15 دقيقة على الأقل.\n"
                "عادةً يُمنع الدخول إذا تأخرت أكثر من 15 دقيقة.\n"
                "بالتوفيق! 🍀"
            ),
            "fr": (
                "**Liste pour l'examen:**\n\n"
                "✅ Obligatoire: carte étudiant (sans carte = pas d'entrée!), stylos bleu/noir, crayons, gomme\n"
                "✅ Si autorisé par l'enseignant: calculatrice non programmable, règle\n"
                "✅ Recommandé: bouteille d'eau transparente, stylos de rechange, montre\n\n"
                "❌ Strictement interdit: téléphone portable, montre connectée, notes/livres (sauf examen ouvert),\n"
                "   calculatrice programmable, écouteurs, tout appareil de communication\n\n"
                "Arrivez au moins 15 minutes à l'avance.\n"
                "L'entrée est généralement refusée après 15 minutes de retard.\n"
                "Bonne chance! 🍀"
            ),
        },
        "keywords": ["exam","bring","required","allowed","need","apporter",
                     "ماذا أحضر","مستلزمات","ما أحتاج"],
        "variants": ["what to bring to exam","exam requirements","quoi apporter à l'examen",
                     "ماذا أحضر للامتحان"],
    },
    # 22. Contact info
    {
        "id": 22, "category": "contact",
        "question": "How can I contact the university?",
        "answers": {
            "en": (
                "**{university_name} – Contact Information:**\n\n"
                "📍 {address}\n"
                "🌐 {website}\n"
                "📧 General: {email_general}\n"
                "☎  {phone_main}\n\n"
                "Key contacts:\n"
                "- Registrar: {email_registrar}\n"
                "- Finance: {email_finance}\n"
                "- IT Support: {email_it}\n"
                "- Student Affairs: {email_student}\n"
                "- Financial Aid: {email_financial_aid}\n"
                "- Library: {email_library}\n\n"
                "Office hours: Sunday–Thursday 8AM–4PM (closed Fri–Sat)\n"
                "Reduced hours during Ramadan."
            ),
            "ar": (
                "**{university_name_ar} – معلومات الاتصال:**\n\n"
                "📍 {address}\n"
                "🌐 {website}\n"
                "📧 عام: {email_general}\n"
                "☎  {phone_main}\n\n"
                "جهات الاتصال الرئيسية:\n"
                "- شؤون التسجيل: {email_registrar}\n"
                "- الشؤون المالية: {email_finance}\n"
                "- الدعم التقني: {email_it}\n"
                "- شؤون الطلاب: {email_student}\n"
                "- المنح الدراسية: {email_financial_aid}\n"
                "- المكتبة: {email_library}\n\n"
                "أوقات العمل: الأحد–الخميس 8ص–4م (مغلق الجمعة–السبت)\n"
                "ساعات مختصرة خلال رمضان."
            ),
            "fr": (
                "**{university_name_fr} – Coordonnées:**\n\n"
                "📍 {address}\n"
                "🌐 {website}\n"
                "📧 Général: {email_general}\n"
                "☎  {phone_main}\n\n"
                "Contacts clés:\n"
                "- Registraire: {email_registrar}\n"
                "- Finance: {email_finance}\n"
                "- Support IT: {email_it}\n"
                "- Scolarité: {email_student}\n"
                "- Bourses: {email_financial_aid}\n"
                "- Bibliothèque: {email_library}\n\n"
                "Horaires: Dimanche–Jeudi 8h–16h (fermé Ven–Sam)\n"
                "Horaires réduits pendant le Ramadan."
            ),
        },
        "keywords": ["contact","phone","email","reach","call","address",
                     "contacter","coordonnées","تواصل","رقم","بريد"],
        "variants": ["contact university","phone number","contacter l'université","كيف أتواصل"],
    },
]


# ---------------------------------------------------------------------------
# FAQMatcher
# ---------------------------------------------------------------------------

class FAQMatcher:
    """NLP-based FAQ matcher – language-agnostic, university-agnostic."""

    def __init__(self):
        self.faqs = _FAQS

    def _preprocess(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        return ' '.join(text.split())

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _keyword_score(self, query: str, faq: Dict) -> float:
        query_words = set(query.split())
        hits = sum(
            1 for kw in faq['keywords']
            if kw.lower() in query or any(kw.lower() in w for w in query_words)
        )
        variant_bonus = 0.3 if any(v.lower() in query for v in faq['variants']) else 0
        return min(hits / max(len(faq['keywords']), 1) + variant_bonus, 1.0)

    def _semantic_score(self, query: str, faq: Dict) -> float:
        q_sim = self._similarity(query, self._preprocess(faq['question']))
        v_sim = max(
            (self._similarity(query, self._preprocess(v)) for v in faq['variants']),
            default=0,
        )
        return max(q_sim, v_sim)

    def find_best_match(self, user_query: str, threshold: float = 0.3) -> Optional[Dict]:
        query = self._preprocess(user_query)
        best, best_score = None, 0.0
        for faq in self.faqs:
            score = self._keyword_score(query, faq) * 0.6 + self._semantic_score(query, faq) * 0.4
            if score > best_score:
                best_score, best = score, faq
        if best_score >= threshold:
            return {'faq': best, 'confidence': round(best_score, 2), 'category': best['category']}
        return None

    def find_multiple_matches(self, user_query: str, top_k: int = 3, threshold: float = 0.25) -> List[Dict]:
        query = self._preprocess(user_query)
        matches = []
        for faq in self.faqs:
            score = self._keyword_score(query, faq) * 0.6 + self._semantic_score(query, faq) * 0.4
            if score >= threshold:
                matches.append({'faq': faq, 'confidence': round(score, 2), 'category': faq['category']})
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:top_k]

    def get_faqs_by_category(self, category: str) -> List[Dict]:
        return [f for f in self.faqs if f['category'] == category]

    def get_all_categories(self) -> List[str]:
        return list({f['category'] for f in self.faqs})


# Singleton
faq_matcher = FAQMatcher()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_faq(query: str, university=None) -> Dict:
    """
    Search FAQ and return the answer in the same language as the query.
    Placeholders in answers are replaced with actual university data.

    Args:
        query:      The user's message.
        university: SQLAlchemy University ORM object (optional).
                    If None, generic placeholder values are used.

    Returns:
        {
          'found': bool,
          'answer': str,          # filled-in, language-matched answer
          'question': str,
          'confidence': float,
          'category': str,
          'language': str,        # 'ar' | 'fr' | 'en'
        }
        or {'found': False, 'language': str, 'message': str}
    """
    lang = detect_language(query)
    match = faq_matcher.find_best_match(query)

    if match:
        faq = match['faq']
        answers = faq.get('answers', {})
        raw_answer = answers.get(lang) or answers.get('en', '')

        # Fill placeholders with university-specific data
        ph = build_placeholders(university)
        answer = fill(raw_answer, ph)

        return {
            'found':      True,
            'answer':     answer,
            'question':   faq['question'],
            'confidence': match['confidence'],
            'category':   match['category'],
            'language':   lang,
        }

    return {
        'found':    False,
        'language': lang,
        'message':  'No FAQ match found. AI will respond.',
    }