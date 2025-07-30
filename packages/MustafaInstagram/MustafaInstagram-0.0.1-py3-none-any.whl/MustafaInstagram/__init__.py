import random
import requests
import user_agent

class Instagram:
    def __init__(self):
        pass

    def generateUsername(self):
        g=random.choice(
                [
                    'azertyuiopmlkjhgfdsqwxcvbn', 
                    'azertyuiopmlkjhgfdsqwxcvbn',
                    'azertyuiopmlkjhgfdsqwxcvbn',
                    'azertyuiopmlkjhgfdsqwxcvbn',
                    'azertyuiopmlkjhgfdsqwxcvbn',
                    'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',  
                    'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',
                    'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',
                    
'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',                'abcdefghijklmnopqrstuvwxyzñ',  
                    'abcdefghijklmnopqrstuvwxyzñ',
                    'abcdefghijklmnopqrstuvwxyzñ',
                    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',  
                    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                    'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                    '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',  
                    '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',
                    '的一是不了人我在有他这为之大来以个中上们到说时国和地要就出会可也你对生能而子那得于着下自之',
                    'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',  
                    'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
                    'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん', 
                    'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
                    'אבגדהוזחטיכלמנסעפצקרשת',
                    'אבגדהוזחטיכלמנסעפצקרשת',
                    'αβγδεζηθικλμνξοπρστυφχψω',  
                    'αβγδεζηθικλμνξοπρστυφχψω',
                    'abcdefghijklmnopqrstuvwxyzç', 
                    'abcdefghijklmnopqrstuvwxyzç',
                    'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',  
                    'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',
                    'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',  
                    'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',
                ]

            )
        keyword=''.join((random.choice(g) for i in range(random.randrange(4,9))))
        cookies = {
                'rur': '"LDC\\05467838469205\\0541758153066:01f72be7578ed09a57bfe3e41c19af58848e0e965e0549f6d1f5a0168a652d2bfa28cd9a"',
            }

        headers = {
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'priority': 'u=1, i',
                'referer': 'https://www.instagram.com/',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
                'sec-ch-ua-full-version-list': '"Chromium";v="128.0.6613.138", "Not;A=Brand";v="24.0.0.0", "Google Chrome";v="128.0.6613.138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': str(user_agent.generate_user_agent()),
                'x-asbd-id': '129477',
                'x-bloks-version-id': '235c9483d007713b45fc75b34c76332d68d579a4300a1db1da94670c3a05089f',
                'x-csrftoken': 'mf3zd6qWxnKgh9BaNRI5Ldpms2NrH62X',
                'x-fb-friendly-name': 'PolarisSearchBoxRefetchableQuery',
                'x-fb-lsd': 'BslibIYRWxn19hyIaPyrZV',
                'x-ig-app-id': '936619743392459',
            }

        data = {
                'variables': '{"data":{"context":"blended","include_reel":"true","query":"'+keyword+'","rank_token":"","search_surface":"web_top_search"},"hasQuery":true}',
                'doc_id': '7935512656557707',
            }
        try:
            response = requests.post('https://www.instagram.com/graphql/query', cookies=cookies, headers=headers, data=data).json()
            
            usernames = []
            # Check if 'data' and 'xdt_api__v1__fbsearch__topsearch_connection' exist in the response
            if 'data' in response and 'xdt_api__v1__fbsearch__topsearch_connection' in response['data']:
                users_data = response['data']['xdt_api__v1__fbsearch__topsearch_connection']['users']
                for i in users_data:
                    if 'user' in i and 'username' in i['user']:
                        usernames.append(i['user']['username'])
            return usernames
        except Exception as e:
            return f"Error generating username: {e}"


