from app import app, db
from models import User, University, Faculty, Department, KnowledgeBase
import sys

def init_database(drop_existing=True):
    with app.app_context():
        if drop_existing:
            print("Dropping all tables...")
            db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("\n=== Initializing Universities ===")
        
        # Batna 2 University
        batna2 = University(
            name='Batna 2 University - Mostefa Ben Boulaïd',
            name_ar='جامعة باتنة 2 - مصطفى بن بولعيد',
            code='BATNA2',
            city='Batna',
            website='https://www.univ-batna2.dz',
            email='contact@univ-batna2.dz',
            phone='+213 33 81 51 33',
            address='Fesdis, Batna 05078, Algeria'
        )
        db.session.add(batna2)
        db.session.flush()
        
        # Algiers 1 University
        algiers1 = University(
            name='University of Algiers 1 - Benyoucef Benkhedda',
            name_ar='جامعة الجزائر 1 - بن يوسف بن خدة',
            code='ALGIERS1',
            city='Algiers',
            website='https://www.univ-alger.dz',
            email='contact@univ-alger.dz',
            phone='+213 21 23 45 67',
            address='2 Rue Didouche Mourad, Algiers, Algeria'
        )
        db.session.add(algiers1)
        db.session.flush()
        
        # Constantine 1 University
        constantine1 = University(
            name='Constantine 1 University - Frères Mentouri',
            name_ar='جامعة قسنطينة 1 - الإخوة منتوري',
            code='CONSTANTINE1',
            city='Constantine',
            website='https://www.umc.edu.dz',
            email='contact@umc.edu.dz',
            phone='+213 31 81 88 00',
            address='Route Ain El Bey, Constantine 25000, Algeria'
        )
        db.session.add(constantine1)
        db.session.flush()
        # Batna 1 University
        batna1 = University(
            name='Batna 1 University - Hadj Lakhdar',
            name_ar='جامعة باتنة 1 - الحاج لخضر',
            code='BATNA1',
            city='Batna',
            website='https://www.univ-batna.dz',
            email='contact@univ-batna.dz',
            phone='+213 33 81 10 30',
            address='Route de Biskra, Batna, Algeria'
        )
        db.session.add(batna1)
        db.session.flush()

        # Biskra University
        biskra = University(
            name='University of Biskra - Mohamed Khider',
            name_ar='جامعة بسكرة - محمد خيضر',
            code='BISKRA',
            city='Biskra',
            website='https://www.univ-biskra.dz',
            email='contact@univ-biskra.dz',
            phone='+213 33 74 68 44',
            address='Biskra, Algeria'
        )
        db.session.add(biskra)
        db.session.flush()

        # Annaba University
        annaba = University(
            name='University of Annaba - Badji Mokhtar',
            name_ar='جامعة عنابة - باجي مختار',
            code='ANNABA',
            city='Annaba',
            website='https://www.univ-annaba.dz',
            email='contact@univ-annaba.dz',
            phone='+213 38 57 02 57',
            address='Annaba, Algeria'
        )
        db.session.add(annaba)
        db.session.flush()

        # Setif 1 University
        setif1 = University(
            name='University of Setif 1 - Ferhat Abbas',
            name_ar='جامعة سطيف 1 - فرحات عباس',
            code='SETIF1',
            city='Setif',
            website='https://www.univ-setif.dz',
            email='contact@univ-setif.dz',
            phone='+213 36 66 11 88',
            address='Setif, Algeria'
        )
        db.session.add(setif1)
        db.session.flush()

        # Setif 2 University
        setif2 = University(
            name='University of Setif 2 - Mohamed Lamine Debaghine',
            name_ar='جامعة سطيف 2 - محمد الأمين دباغين',
            code='SETIF2',
            city='Setif',
            website='https://www.univ-setif2.dz',
            email='contact@univ-setif2.dz',
            phone='+213 36 66 11 89',
            address='Setif, Algeria'
        )
        db.session.add(setif2)
        db.session.flush()

        # Bejaia University
        bejaia = University(
            name='University of Bejaia - Abderrahmane Mira',
            name_ar='جامعة بجاية - عبد الرحمان ميرة',
            code='BEJAIA',
            city='Bejaia',
            website='https://www.univ-bejaia.dz',
            email='contact@univ-bejaia.dz',
            phone='+213 34 21 09 10',
            address='Bejaia, Algeria'
        )
        db.session.add(bejaia)
        db.session.flush()

        # Tizi Ouzou University
        tizi = University(
            name='University of Tizi Ouzou - Mouloud Mammeri',
            name_ar='جامعة تيزي وزو - مولود معمري',
            code='TIZI',
            city='Tizi Ouzou',
            website='https://www.ummto.dz',
            email='contact@ummto.dz',
            phone='+213 26 11 55 11',
            address='Tizi Ouzou, Algeria'
        )
        db.session.add(tizi)
        db.session.flush()

        # Blida 1 University
        blida1 = University(
            name='University of Blida 1 - Saad Dahlab',
            name_ar='جامعة البليدة 1 - سعد دحلب',
            code='BLIDA1',
            city='Blida',
            website='https://www.univ-blida.dz',
            email='contact@univ-blida.dz',
            phone='+213 25 43 38 38',
            address='Blida, Algeria'
        )
        db.session.add(blida1)
        db.session.flush()

        # Blida 2 University
        blida2 = University(
            name='University of Blida 2 - Lounici Ali',
            name_ar='جامعة البليدة 2 - لونيسي علي',
            code='BLIDA2',
            city='Blida',
            website='https://www.univ-blida2.dz',
            email='contact@univ-blida2.dz',
            phone='+213 25 43 38 39',
            address='Blida, Algeria'
        )
        db.session.add(blida2)
        db.session.flush()

        # Djelfa University
        djelfa = University(
            name='University of Djelfa - Ziane Achour',
            name_ar='جامعة الجلفة - زيان عاشور',
            code='DJELFA',
            city='Djelfa',
            website='https://www.univ-djelfa.dz',
            email='contact@univ-djelfa.dz',
            phone='+213 27 92 16 14',
            address='Djelfa, Algeria'
        )
        db.session.add(djelfa)
        db.session.flush()

        # Laghouat University
        laghouat = University(
            name='University of Laghouat - Amar Telidji',
            name_ar='جامعة الأغواط - عمار ثليجي',
            code='LAGHOUAT',
            city='Laghouat',
            website='https://www.lagh-univ.dz',
            email='contact@lagh-univ.dz',
            phone='+213 29 93 31 00',
            address='Laghouat, Algeria'
        )
        db.session.add(laghouat)
        db.session.flush()

        # Ouargla University
        ouargla = University(
            name='University of Ouargla - Kasdi Merbah',
            name_ar='جامعة ورقلة - قاصدي مرباح',
            code='OUARGLA',
            city='Ouargla',
            website='https://www.univ-ouargla.dz',
            email='contact@univ-ouargla.dz',
            phone='+213 29 71 56 31',
            address='Ouargla, Algeria'
        )
        db.session.add(ouargla)
        db.session.flush()

        # Tlemcen University
        tlemcen = University(
            name='University of Tlemcen - Abou Bekr Belkaid',
            name_ar='جامعة تلمسان - أبو بكر بلقايد',
            code='TLEMCEN',
            city='Tlemcen',
            website='https://www.univ-tlemcen.dz',
            email='contact@univ-tlemcen.dz',
            phone='+213 43 21 51 33',
            address='Tlemcen, Algeria'
        )
        db.session.add(tlemcen)
        db.session.flush()

        # Oran 1 University
        oran1 = University(
            name='University of Oran 1 - Ahmed Ben Bella',
            name_ar='جامعة وهران 1 - أحمد بن بلة',
            code='ORAN1',
            city='Oran',
            website='https://www.univ-oran1.dz',
            email='contact@univ-oran1.dz',
            phone='+213 41 51 93 02',
            address='Oran, Algeria'
        )
        db.session.add(oran1)
        db.session.flush()

        # Oran 2 University
        oran2 = University(
            name='University of Oran 2 - Mohamed Ben Ahmed',
            name_ar='جامعة وهران 2 - محمد بن أحمد',
            code='ORAN2',
            city='Oran',
            website='https://www.univ-oran2.dz',
            email='contact@univ-oran2.dz',
            phone='+213 41 51 93 03',
            address='Oran, Algeria'
        )
        db.session.add(oran2)
        db.session.flush()

        # Mostaganem University
        mostaganem = University(
            name='University of Mostaganem - Abdelhamid Ibn Badis',
            name_ar='جامعة مستغانم - عبد الحميد بن باديس',
            code='MOSTA',
            city='Mostaganem',
            website='https://www.univ-mosta.dz',
            email='contact@univ-mosta.dz',
            phone='+213 45 42 11 12',
            address='Mostaganem, Algeria'
        )
        db.session.add(mostaganem)
        db.session.flush()

        # Relizane University
        relizane = University(
            name='University of Relizane - Ahmed Zabana',
            name_ar='جامعة غليزان - أحمد زبانة',
            code='RELIZANE',
            city='Relizane',
            website='https://www.univ-relizane.dz',
            email='contact@univ-relizane.dz',
            phone='+213 46 71 25 00',
            address='Relizane, Algeria'
        )
        db.session.add(relizane)
        db.session.flush()

        # Sidi Bel Abbes University
        sba = University(
            name='University of Sidi Bel Abbes - Djillali Liabes',
            name_ar='جامعة سيدي بلعباس - جيلالي اليابس',
            code='SBA',
            city='Sidi Bel Abbes',
            website='https://www.univ-sba.dz',
            email='contact@univ-sba.dz',
            phone='+213 48 55 43 43',
            address='Sidi Bel Abbes, Algeria'
        )
        db.session.add(sba)
        db.session.flush()

        # Guelma University
        guelma = University(
            name='University of Guelma - 8 May 1945',
            name_ar='جامعة قالمة - 8 ماي 1945',
            code='GUELMA',
            city='Guelma',
            website='https://www.univ-guelma.dz',
            email='contact@univ-guelma.dz',
            phone='+213 37 20 17 00',
            address='Guelma, Algeria'
        )
        db.session.add(guelma)
        db.session.flush()

        # Skikda University
        skikda = University(
            name='University of Skikda - 20 August 1955',
            name_ar='جامعة سكيكدة - 20 أوت 1955',
            code='SKIKDA',
            city='Skikda',
            website='https://www.univ-skikda.dz',
            email='contact@univ-skikda.dz',
            phone='+213 38 72 32 51',
            address='Skikda, Algeria'
        )
        db.session.add(skikda)
        db.session.flush()

        # El Oued University
        eloued = University(
            name='University of El Oued - Hamma Lakhdar',
            name_ar='جامعة الوادي - حمة لخضر',
            code='ELOUED',
            city='El Oued',
            website='https://www.univ-eloued.dz',
            email='contact@univ-eloued.dz',
            phone='+213 32 20 17 00',
            address='El Oued, Algeria'
        )
        db.session.add(eloued)
        db.session.flush()

        # Khenchela University
        khenchela = University(
            name='University of Khenchela - Abbas Laghrour',
            name_ar='جامعة خنشلة - عباس لغرور',
            code='KHENCHELA',
            city='Khenchela',
            website='https://www.univ-khenchela.dz',
            email='contact@univ-khenchela.dz',
            phone='+213 32 59 00 50',
            address='Khenchela, Algeria'
        )
        db.session.add(khenchela)
        db.session.flush()

        # Souk Ahras University
        soukahras = University(
            name='University of Souk Ahras - Mohamed Cherif Messaadia',
            name_ar='جامعة سوق أهراس - محمد الشريف مساعدية',
            code='SOUKAHRAS',
            city='Souk Ahras',
            website='https://www.univ-soukahras.dz',
            email='contact@univ-soukahras.dz',
            phone='+213 37 85 23 23',
            address='Souk Ahras, Algeria'
        )
        db.session.add(soukahras)
        db.session.flush()

        # Adrar University
        adrar = University(
            name='University of Adrar - Ahmed Draia',
            name_ar='جامعة أدرار - أحمد دراية',
            code='ADRAR',
            city='Adrar',
            website='https://www.univ-adrar.dz',
            email='contact@univ-adrar.dz',
            phone='+213 49 96 11 22',
            address='Adrar, Algeria'
        )
        db.session.add(adrar)
        db.session.flush()

        # Bechar University
        bechar = University(
            name='University of Bechar - Tahri Mohamed',
            name_ar='جامعة بشار - طاهري محمد',
            code='BECHAR',
            city='Bechar',
            website='https://www.univ-bechar.dz',
            email='contact@univ-bechar.dz',
            phone='+213 49 81 11 22',
            address='Bechar, Algeria'
        )
        db.session.add(bechar)
        db.session.flush()

        # Tindouf University Center
        tindouf = University(
            name='University Center of Tindouf',
            name_ar='المركز الجامعي تندوف',
            code='TINDOUF',
            city='Tindouf',
            website='https://www.cu-tindouf.dz',
            email=None,
            phone=None,
            address='Tindouf, Algeria'
        )
        db.session.add(tindouf)
        db.session.flush()

        # Ghardaia University
        ghardaia = University(
            name='University of Ghardaia',
            name_ar='جامعة غرداية',
            code='GHARDAIA',
            city='Ghardaia',
            website='https://www.univ-ghardaia.dz',
            email='contact@univ-ghardaia.dz',
            phone='+213 29 21 17 00',
            address='Ghardaia, Algeria'
        )
        db.session.add(ghardaia)
        db.session.flush()

        # Illizi University Center
        illizi = University(
            name='University Center of Illizi',
            name_ar='المركز الجامعي إليزي',
            code='ILLIZI',
            city='Illizi',
            website='https://www.cu-illizi.dz',
            email=None,
            phone=None,
            address='Illizi, Algeria'
        )
        db.session.add(illizi)
        db.session.flush()

        # Bordj Bou Arreridj University
        bordj = University(
            name='University of Bordj Bou Arreridj - Mohamed El Bachir El Ibrahimi',
            name_ar='جامعة برج بوعريريج - محمد البشير الإبراهيمي',
            code='BBA',
            city='Bordj Bou Arreridj',
            website='https://www.univ-bba.dz',
            email='contact@univ-bba.dz',
            phone='+213 35 68 45 45',
            address='Bordj Bou Arreridj, Algeria'
        )
        db.session.add(bordj)
        db.session.flush()

        # Medea University
        medea = University(
            name='University of Medea - Yahia Fares',
            name_ar='جامعة المدية - يحي فارس',
            code='MEDEA',
            city='Medea',
            website='https://www.univ-medea.dz',
            email='contact@univ-medea.dz',
            phone='+213 25 58 55 55',
            address='Medea, Algeria'
        )
        db.session.add(medea)
        db.session.flush()

        # Bouira University
        bouira = University(
            name='University of Bouira - Akli Mohand Oulhadj',
            name_ar='جامعة البويرة - أكلي محند أولحاج',
            code='BOUIRA',
            city='Bouira',
            website='https://www.univ-bouira.dz',
            email='contact@univ-bouira.dz',
            phone='+213 26 91 24 24',
            address='Bouira, Algeria'
        )
        db.session.add(bouira)
        db.session.flush()

        # Chlef University
        chlef = University(
            name='University of Chlef - Hassiba Ben Bouali',
            name_ar='جامعة الشلف - حسيبة بن بوعلي',
            code='CHLEF',
            city='Chlef',
            website='https://www.univ-chlef.dz',
            email='contact@univ-chlef.dz',
            phone='+213 27 72 17 00',
            address='Chlef, Algeria'
        )
        db.session.add(chlef)
        db.session.flush()

        # Mascara University
        mascara = University(
            name='University of Mascara - Mustapha Stambouli',
            name_ar='جامعة معسكر - مصطفى اسطمبولي',
            code='MASCARA',
            city='Mascara',
            website='https://www.univ-mascara.dz',
            email='contact@univ-mascara.dz',
            phone='+213 45 70 17 00',
            address='Mascara, Algeria'
        )
        db.session.add(mascara)
        db.session.flush()

        # Tiaret University
        tiaret = University(
            name='University of Tiaret - Ibn Khaldoun',
            name_ar='جامعة تيارت - ابن خلدون',
            code='TIARET',
            city='Tiaret',
            website='https://www.univ-tiaret.dz',
            email='contact@univ-tiaret.dz',
            phone='+213 46 41 17 00',
            address='Tiaret, Algeria'
        )
        db.session.add(tiaret)
        db.session.flush()

        # Saida University
        saida = University(
            name='University of Saida - Dr Moulay Tahar',
            name_ar='جامعة سعيدة - الدكتور مولاي الطاهر',
            code='SAIDA',
            city='Saida',
            website='https://www.univ-saida.dz',
            email='contact@univ-saida.dz',
            phone='+213 48 21 17 00',
            address='Saida, Algeria'
        )
        db.session.add(saida)
        db.session.flush()

        # El Bayadh University Center
        elbayadh = University(
            name='University Center of El Bayadh',
            name_ar='المركز الجامعي البيض',
            code='ELBAYADH',
            city='El Bayadh',
            website='https://www.cu-elbayadh.dz',
            email=None,
            phone=None,
            address='El Bayadh, Algeria'
        )
        db.session.add(elbayadh)
        db.session.flush()

        # Naama University Center
        naama = University(
            name='University Center of Naama',
            name_ar='المركز الجامعي النعامة',
            code='NAAMA',
            city='Naama',
            website='https://www.cu-naama.dz',
            email=None,
            phone=None,
            address='Naama, Algeria'
        )
        db.session.add(naama)
        db.session.flush()

        # Ain Temouchent University
        temouchent = University(
            name='University of Ain Temouchent - Belhadj Bouchaib',
            name_ar='جامعة عين تموشنت - بلحاج بوشعيب',
            code='TEMOUCHENT',
            city='Ain Temouchent',
            website='https://www.univ-temouchent.dz',
            email='contact@univ-temouchent.dz',
            phone='+213 43 90 17 00',
            address='Ain Temouchent, Algeria'
        )
        db.session.add(temouchent)
        db.session.flush()

        # Tissemsilt University Center
        tissemsilt = University(
            name='University Center of Tissemsilt',
            name_ar='المركز الجامعي تيسمسيلت',
            code='TISSEMSILT',
            city='Tissemsilt',
            website='https://www.cu-tissemsilt.dz',
            email=None,
            phone=None,
            address='Tissemsilt, Algeria'
        )
        db.session.add(tissemsilt)
        db.session.flush()

        # Mila University Center
        mila = University(
            name='University Center of Mila',
            name_ar='المركز الجامعي ميلة',
            code='MILA',
            city='Mila',
            website='https://www.cu-mila.dz',
            email=None,
            phone=None,
            address='Mila, Algeria'
        )
        db.session.add(mila)
        db.session.flush()

        # Tipaza University Center
        tipaza = University(
            name='University Center of Tipaza',
            name_ar='المركز الجامعي تيبازة',
            code='TIPAZA',
            city='Tipaza',
            website='https://www.cu-tipaza.dz',
            email=None,
            phone=None,
            address='Tipaza, Algeria'
        )
        db.session.add(tipaza)
        db.session.flush()

        # Maghnia University Center
        maghnia = University(
            name='University Center of Maghnia',
            name_ar='المركز الجامعي مغنية',
            code='MAGHNIA',
            city='Maghnia',
            website='https://www.cu-maghnia.dz',
            email=None,
            phone=None,
            address='Maghnia, Algeria'
        )
        db.session.add(maghnia)
        db.session.flush()

        # Koléa University Center
        kolea = University(
            name='University Center of Koléa',
            name_ar='المركز الجامعي القليعة',
            code='KOLEA',
            city='Tipaza',
            website='https://www.cu-kolea.dz',
            email=None,
            phone=None,
            address='Kolea, Algeria'
        )
        db.session.add(kolea)
        db.session.flush()
        
        # University of El Tarf
        eltarf = University(
            name='University of El Tarf - Chadli Bendjedid',
            name_ar='جامعة الطارف - الشاذلي بن جديد',
            code='ELTARF',
            city='El Tarf',
            website='https://www.univ-eltarf.dz',
            email='contact@univ-eltarf.dz',
            phone='+213 38 60 17 00',
            address='El Tarf, Algeria'
        )
        db.session.add(eltarf)
        db.session.flush()

        # University Center of Ain Defla
        aindefla = University(
            name='University Center of Ain Defla',
            name_ar='المركز الجامعي عين الدفلى',
            code='AINDEFLA',
            city='Ain Defla',
            website='https://www.cu-aindefla.dz',
            email=None,
            phone=None,
            address='Ain Defla, Algeria'
        )
        db.session.add(aindefla)
        db.session.flush()

        # University Center of Barika
        barika = University(
            name='University Center of Barika',
            name_ar='المركز الجامعي بريكة',
            code='BARIKA',
            city='Batna',
            website='https://www.cu-barika.dz',
            email=None,
            phone=None,
            address='Barika, Batna, Algeria'
        )
        db.session.add(barika)
        db.session.flush()

        # University Center of Ain Temouchent (Extension)
        temouchent_cu = University(
            name='University Center of Ain Temouchent',
            name_ar='المركز الجامعي عين تموشنت',
            code='CU_TEMOUCHENT',
            city='Ain Temouchent',
            website='https://www.cu-temouchent.dz',
            email=None,
            phone=None,
            address='Ain Temouchent, Algeria'
        )
        db.session.add(temouchent_cu)
        db.session.flush()

        # University Center of Touggourt
        touggourt = University(
            name='University Center of Touggourt',
            name_ar='المركز الجامعي تقرت',
            code='TOUGGOURT',
            city='Touggourt',
            website='https://www.cu-touggourt.dz',
            email=None,
            phone=None,
            address='Touggourt, Algeria'
        )
        db.session.add(touggourt)
        db.session.flush()

        # University Center of Bordj Badji Mokhtar
        bbm = University(
            name='University Center of Bordj Badji Mokhtar',
            name_ar='المركز الجامعي برج باجي مختار',
            code='BBM',
            city='Bordj Badji Mokhtar',
            website='https://www.cu-bbm.dz',
            email=None,
            phone=None,
            address='Bordj Badji Mokhtar, Algeria'
        )
        db.session.add(bbm)
        db.session.flush()

        # University Center of Djanet
        djanet = University(
            name='University Center of Djanet',
            name_ar='المركز الجامعي جانت',
            code='DJANET',
            city='Djanet',
            website='https://www.cu-djanet.dz',
            email=None,
            phone=None,
            address='Djanet, Algeria'
        )
        db.session.add(djanet)
        db.session.flush()

        # University Center of Timimoun
        timimoun = University(
            name='University Center of Timimoun',
            name_ar='المركز الجامعي تيميمون',
            code='TIMIMOUN',
            city='Timimoun',
            website='https://www.cu-timimoun.dz',
            email=None,
            phone=None,
            address='Timimoun, Algeria'
        )
        db.session.add(timimoun)
        db.session.flush()

        # University Center of Ouled Djellal
        ouledd = University(
            name='University Center of Ouled Djellal',
            name_ar='المركز الجامعي أولاد جلال',
            code='OULEDDJELLAL',
            city='Biskra',
            website='https://www.cu-ouleddjellal.dz',
            email=None,
            phone=None,
            address='Ouled Djellal, Algeria'
        )
        db.session.add(ouledd)
        db.session.flush()

        # University Center of El Meghaier
        meghaier = University(
            name='University Center of El Meghaier',
            name_ar='المركز الجامعي المغير',
            code='MEGHAIER',
            city='El Meghaier',
            website='https://www.cu-meghaier.dz',
            email=None,
            phone=None,
            address='El Meghaier, Algeria'
        )
        db.session.add(meghaier)
        db.session.flush()

        # University Center of Beni Abbas
        beniabbes = University(
            name='University Center of Beni Abbas',
            name_ar='المركز الجامعي بني عباس',
            code='BENIABBES',
            city='Beni Abbas',
            website='https://www.cu-beniabbes.dz',
            email=None,
            phone=None,
            address='Beni Abbas, Algeria'
        )
        db.session.add(beniabbes)
        db.session.flush()
        
        #  Faculties and Departments
        print("\n=== Creating Faculties and Departments ===")
        
        # ===== BATNA 2 UNIVERSITY =====
        # Faculty 1: Faculty of Science
        fac_science_batna2 = Faculty(
            name='Faculty of Science',
            name_ar='كلية العلوم',
            name_fr='Faculté des Sciences',
            code='FS_BATNA2',
            university_id=batna2.id,
            dean='Prof. Ahmed Karim',
            email='science@univ-batna2.dz',
            phone='+213 33 81 51 33',
            building='Building A'
        )
        db.session.add(fac_science_batna2)
        db.session.flush()
        
        # Departments for Faculty of Science
        dept_cs_batna2 = Department(
            name='Computer Science',
            name_ar='علوم الحاسبات',
            name_fr='Informatique',
            code='CS_BATNA2',
            university_id=batna2.id,
            faculty_id=fac_science_batna2.id,
            head_of_department='Prof. Mohamed Ali',
            email='cs@univ-batna2.dz',
            building='Building A - Floor 2'
        )
        db.session.add(dept_cs_batna2)
        db.session.flush()
        
        dept_math_batna2 = Department(
            name='Mathematics',
            name_ar='الرياضيات',
            name_fr='Mathématiques',
            code='MATH_BATNA2',
            university_id=batna2.id,
            faculty_id=fac_science_batna2.id,
            head_of_department='Prof. Fatima Khan',
            email='math@univ-batna2.dz',
            building='Building A - Floor 3'
        )
        db.session.add(dept_math_batna2)
        db.session.flush()
        
        # Faculty 2: Faculty of Engineering
        fac_eng_batna2 = Faculty(
            name='Faculty of Engineering',
            name_ar='كلية الهندسة',
            name_fr='Faculté de Génie',
            code='FE_BATNA2',
            university_id=batna2.id,
            dean='Prof. Hassan Ibrahim',
            email='engineering@univ-batna2.dz',
            phone='+213 33 81 51 34',
            building='Building B'
        )
        db.session.add(fac_eng_batna2)
        db.session.flush()
        
        # Departments for Faculty of Engineering
        dept_civil_batna2 = Department(
            name='Civil Engineering',
            name_ar='الهندسة المدنية',
            name_fr='Génie Civil',
            code='CE_BATNA2',
            university_id=batna2.id,
            faculty_id=fac_eng_batna2.id,
            head_of_department='Prof. Yousef Omar',
            email='civil@univ-batna2.dz',
            building='Building B - Floor 1'
        )
        db.session.add(dept_civil_batna2)
        db.session.flush()
        
        dept_electrical_batna2 = Department(
            name='Electrical Engineering',
            name_ar='الهندسة الكهربائية',
            name_fr='Génie Électrique',
            code='EE_BATNA2',
            university_id=batna2.id,
            faculty_id=fac_eng_batna2.id,
            head_of_department='Prof. Leila Amir',
            email='electrical@univ-batna2.dz',
            building='Building B - Floor 2'
        )
        db.session.add(dept_electrical_batna2)
        db.session.flush()
        
        # ===== ALGIERS 1 UNIVERSITY =====
        # Faculty 1: Faculty of Letters
        fac_letters_algiers = Faculty(
            name='Faculty of Letters and Languages',
            name_ar='كلية الآداب واللغات',
            name_fr='Faculté des Lettres et Langues',
            code='FL_ALGIERS1',
            university_id=algiers1.id,
            dean='Prof. Rachid Saïd',
            email='letters@univ-alger.dz',
            phone='+213 21 23 45 67',
            building='Building D'
        )
        db.session.add(fac_letters_algiers)
        db.session.flush()
        
        # Departments for Faculty of Letters
        dept_english_algiers = Department(
            name='English Literature',
            name_ar='اللغة الإنجليزية والأدب',
            name_fr='Littérature Anglaise',
            code='ENG_ALGIERS1',
            university_id=algiers1.id,
            faculty_id=fac_letters_algiers.id,
            head_of_department='Prof. Samia Benali',
            email='english@univ-alger.dz',
            building='Building D - Floor 1'
        )
        db.session.add(dept_english_algiers)
        db.session.flush()
        
        dept_french_algiers = Department(
            name='French Literature',
            name_ar='اللغة الفرنسية والأدب',
            name_fr='Littérature Française',
            code='FR_ALGIERS1',
            university_id=algiers1.id,
            faculty_id=fac_letters_algiers.id,
            head_of_department='Prof. Nadia Fouad',
            email='french@univ-alger.dz',
            building='Building D - Floor 2'
        )
        db.session.add(dept_french_algiers)
        db.session.flush()
        
        # Faculty 2: Faculty of Law
        fac_law_algiers = Faculty(
            name='Faculty of Law',
            name_ar='كلية الحقوق',
            name_fr='Faculté de Droit',
            code='FLW_ALGIERS1',
            university_id=algiers1.id,
            dean='Prof. Karim Tabbane',
            email='law@univ-alger.dz',
            phone='+213 21 23 45 68',
            building='Building E'
        )
        db.session.add(fac_law_algiers)
        db.session.flush()
        
        # Departments for Faculty of Law
        dept_private_law_algiers = Department(
            name='Private Law',
            name_ar='القانون الخاص',
            name_fr='Droit Privé',
            code='PL_ALGIERS1',
            university_id=algiers1.id,
            faculty_id=fac_law_algiers.id,
            head_of_department='Prof. Amir Hassan',
            email='private-law@univ-alger.dz',
            building='Building E - Floor 1'
        )
        db.session.add(dept_private_law_algiers)
        db.session.flush()
        
        dept_public_law_algiers = Department(
            name='Public Law',
            name_ar='القانون العام',
            name_fr='Droit Public',
            code='PBL_ALGIERS1',
            university_id=algiers1.id,
            faculty_id=fac_law_algiers.id,
            head_of_department='Prof. Souad Benmansour',
            email='public-law@univ-alger.dz',
            building='Building E - Floor 2'
        )
        db.session.add(dept_public_law_algiers)
        db.session.flush()

        # ===== CONSTANTINE 1 UNIVERSITY =====
        # Faculty 1: Faculty of Sciences
        fac_sci_constantine = Faculty(
            name='Faculty of Exact Sciences',
            name_ar='كلية العلوم الدقيقة',
            name_fr='Faculté des Sciences Exactes',
            code='FSE_CONST1',
            university_id=constantine1.id,
            dean='Prof. Jamal Medina',
            email='science@umc.edu.dz',
            phone='+213 31 81 88 00',
            building='Building F'
        )
        db.session.add(fac_sci_constantine)
        db.session.flush()
        
        # Departments for Faculty of Sciences
        dept_physics_const = Department(
            name='Physics',
            name_ar='الفيزياء',
            name_fr='Physique',
            code='PHY_CONST1',
            university_id=constantine1.id,
            faculty_id=fac_sci_constantine.id,
            head_of_department='Prof. Samir Tatar',
            email='physics@umc.edu.dz',
            building='Building F - Floor 1'
        )
        db.session.add(dept_physics_const)
        db.session.flush()
        
        dept_chemistry_const = Department(
            name='Chemistry',
            name_ar='الكيمياء',
            name_fr='Chimie',
            code='CHEM_CONST1',
            university_id=constantine1.id,
            faculty_id=fac_sci_constantine.id,
            head_of_department='Prof. Hana Abdellatif',
            email='chemistry@umc.edu.dz',
            building='Building F - Floor 2'
        )
        db.session.add(dept_chemistry_const)
        db.session.flush()
        
        # Faculty 2: Faculty of Medicine
        fac_med_constantine = Faculty(
            name='Faculty of Medicine',
            name_ar='كلية الطب',
            name_fr='Faculté de Médecine',
            code='FM_CONST1',
            university_id=constantine1.id,
            dean='Prof. Najib Salma',
            email='medicine@umc.edu.dz',
            phone='+213 31 81 88 01',
            building='Building G'
        )
        db.session.add(fac_med_constantine)
        db.session.flush()
        
        # Departments for Faculty of Medicine
        dept_general_med = Department(
            name='General Medicine',
            name_ar='الطب العام',
            name_fr='Médecine Générale',
            code='GM_CONST1',
            university_id=constantine1.id,
            faculty_id=fac_med_constantine.id,
            head_of_department='Prof. Khalil Berghout',
            email='gen-medicine@umc.edu.dz',
            building='Building G - Floor 1'
        )
        db.session.add(dept_general_med)
        db.session.flush()
        
        dept_surgery = Department(
            name='Surgery',
            name_ar='الجراحة',
            name_fr='Chirurgie',
            code='SUR_CONST1',
            university_id=constantine1.id,
            faculty_id=fac_med_constantine.id,
            head_of_department='Prof. Tariq Amoun',
            email='surgery@umc.edu.dz',
            building='Building G - Floor 2'
        )
        db.session.add(dept_surgery)
        db.session.flush()
        
        print("✓ Created Faculties and Departments successfully")
        db.session.flush()
        # Create test user
        print("\n=== Creating Test User ===")
        test_user = User(
            username='test_student',
            email='test@university.com',
            full_name='Test Student',
            student_id='202400001',
            university_id=batna2.id,
            faculty_id=fac_science_batna2.id,
            department_id=dept_cs_batna2.id,
            is_verified=True,
            role='student'
        )
        test_user.set_password('Test123!')
        db.session.add(test_user)
        print("✓ Created test user: test@university.com / Test123!")
        
        # Create admin user (university admin for Batna 2)
        admin_user = User(
            username='admin',
            email='admin@university.com',
            full_name='Admin User',
            university_id=batna2.id,
            is_verified=True,
            is_admin=True,
            role='university_admin'
        )
        admin_user.set_password('Admin123!')
        db.session.add(admin_user)
        print("✓ Created university admin: admin@university.com / Admin123!")
        
        # Create super admin user
        super_admin = User(
            username='superadmin',
            email='superadmin@system.com',
            full_name='Super Administrator',
            university_id=None, 
            is_verified=True,
            is_admin=True,
            role='super_admin'
        )
        super_admin.set_password('Super123!')
        db.session.add(super_admin)
        print("✓ Created super admin: superadmin@system.com / Super123!")
        
        # Add sample knowledge base entries
        print("\n=== Creating Knowledge Base Entries ===")
        kb_entries = [
            {
                'university_id': batna2.id,
                'title': 'Registration Process',
                'content': 'Students must register online through the university portal during the registration period.',
                'category': 'registration',
                "tags": "registration,enroll,signup"
            },
            {
                'university_id': batna2.id,
                'title': 'Computer Science Curriculum',
                'content': 'The CS department offers programs in AI, Networks, Databases, and Software Engineering.',
                'category': 'academic',
                'tags': ['computer science', 'cs', 'curriculum', 'program']
            }
        ]
        
        for kb_data in kb_entries:
         # Convert tags list to string if needed
          if isinstance(kb_data.get("tags"), list):
           kb_data["tags"] = ",".join(kb_data["tags"])

          kb = KnowledgeBase(**kb_data)
          db.session.add(kb)
        
        print(f"✓ Created {len(kb_entries)} knowledge base entries")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   Universities: {University.query.count()}")
        print(f"   Faculties: {Faculty.query.count()}")
        print(f"   Departments: {Department.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Knowledge Base: {KnowledgeBase.query.count()}")
        print("\n🔐 Test Credentials:")
        print("   Student: test@university.com / Test123!")
        print("   University Admin (Batna 2): admin@university.com / Admin123!")
        print("   Super Admin: superadmin@system.com / Super123!")
        print("\n✅ System ready for use!")

if __name__ == '__main__':
    import sys
    
    # Check if update mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        print("\n⚠️  UPDATE MODE: Existing data will be preserved")
        print("This will create tables if they don't exist but won't drop existing ones.\n")
        init_database(drop_existing=False)
    else:
        print("\n⚠️  FRESH INSTALL MODE: All existing data will be deleted")
        response = input("Continue? This will DELETE all existing data! (yes/no): ")
        if response.lower() == 'yes':
            init_database(drop_existing=True)
        else:
            print("Initialization cancelled.")
