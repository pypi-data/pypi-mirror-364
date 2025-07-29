# Sferum API Interface

The Sferum API Interface provides methods to interact with the VK messaging service through API endpoints. This project includes functions for sending messages, retrieving user history, and executing JS-like code code on the server.

## Getting Started

### Prerequisites

- Python 3.x

### Instaling

To install this lib run this in terminal:
```bash
pip install SferumBridge
```

### Obtaining the `remixdsid` Cookie

To interact with VK's API, you'll need to authenticate your session and obtain the `remixdsid` cookie. Follow these steps:

1. Open your web browser and go to [sferum web version](https://web.vk.me).
   
2. Log in to your VK account if you haven't already.

3. After logging in, open the Developer Tools in your web browser (right-click anywhere on the page and select "Inspect" or press `F12`).

4. Navigate to the "Application" tab in Developer Tools.

5. On the left sidebar, find and click on "Cookies" under the "Storage" section. You should see a list of cookies that belong to the `https://web.vk.me` domain.

6. Look for the `remixdsid` cookie. This cookie is usually a long alphanumeric string.

7. Copy the value of the `remixdsid` cookie. You will use this value to authenticate your requests in the SferumAPI class.

## Using the Sferum API Interface

### Initializing the SferumAPI class

To create an instance of the SferumAPI, you need to pass the `remixdsid` obtained from the previous step:

```python
import SferumBridge

remixdsid = 'YOUR_REMIXDSID_COOKIE_HERE'
api = SferumAPI(remixdsid)
```

### Available Methods

`peer_id` is a chat id. You can get it from the URL:
web.vk.me/convo/YOUR_CHAT_ID

1. **Sending a Message:**

   To send a message, use:
   ```python
   response = api.send_message(peer_id=12345678, text="Hello, World!")
   ```

2. **Deleting a Message:**

   To delete a message, use:
   ```python
   response = api.delete_message(peer_id=12345678, message_conversation_id=321)
   ```

3. **Retrieving Message History:**

   To retrieve message history, use:
   ```python
   response = api.get_history(peer_id=12345678, count=20)
   ```

4. **Executing Code:**

   To execute a small piece of JS-like code on the server, use:
   ```python
   response = api.execute(code="""
        var res0=API.messages.delete({"peer_id":2000000002,"cmids":"152","delete_for_all":1,"spam":0,"group_id":0,"lang":"ru"});
        return [res0];
   """)
   ```

   You can use `fork()` to run task in background and `wait()` to wait it
   I found out you can make only 999 cycles in `while` loop and 25 API requests

   Here`s more complicated example:
    ```python
   response = api.execute(code="""
        return [  
            wait(fork(  
                API.users.get({    
                    user_ids: 1058611848,    
                    fields: 'photo_100,photo_200,sex,screen_name,first_name_gen,is_nft,animated_avatar,custom_names_for_calls',  
                })
            )),  
            API.calls.getSettings({}),
        ];  
   """)
   ```

---------

# А теперь на русском

Интерфейс API Sferum предоставляет методы для взаимодействия с сервисом обмена сообщениями VK через API-эндпоинты. Этот проект включает функции для отправки сообщений, получения истории пользователей и выполнения кода, подобного JS, на сервере.

## Начало работы

### Необходимые условия

- Python 3.x

### Установка

Чтобы установить эту библиотеку, выполните следующую команду в терминале:
```bash
pip install SferumBridge
```

### Получение cookie `remixdsid`

Чтобы взаимодействовать с API VK, вам необходимо аутентифицировать сессию и получить cookie `remixdsid`. Следуйте этим шагам:

1. Откройте веб-браузер и перейдите на [веб-версию sferum](https://web.vk.me).
   
2. Войдите в свою учетную запись VK, если еще не сделали этого.

3. После входа откройте Инструменты разработчика в веб-браузере (щелкните правой кнопкой мыши на любой области страницы и выберите "Просмотреть код" или нажмите `F12`).

4. Перейдите на вкладку "Приложение" в Инструментах разработчика.

5. В левой боковой панели найдите и кликните на "Cookies" в разделе "Хранилище". Вы должны увидеть список cookie, принадлежащих домену `https://web.vk.me`.

6. Найдите куку `remixdsid`. Эта кука обычно представляет собой длинную строку из буквенно-цифровых символов.

7. Скопируйте значение куки `remixdsid`. Это значение вам понадобится для аутентификации ваших запросов в классе SferumAPI.

## Использование интерфейса API Sferum

### Инициализация класса SferumAPI

Чтобы создать экземпляр SferumAPI, вы должны передать `remixdsid`, полученный на предыдущем шаге:

```python
import SferumBridge

remixdsid = 'ВАША_COOKIE_REMIXDSID_ЗДЕСЬ'
api = SferumAPI(remixdsid)
```

### Доступные методы

`peer_id` - это ID чата. Вы можете получить его из URL:
web.vk.me/convo/YOUR_CHAT_ID

1. **Отправка сообщения:**

   Чтобы отправить сообщение, используйте:
   ```python
   response = api.send_message(peer_id=12345678, text="Привет, мир!")
   ```

2. **Удаление сообщения:**

   Чтобы удалить сообщение, используйте:
   ```python
   response = api.delete_message(peer_id=12345678, message_conversation_id=321)
   ```

3. **Получение истории сообщений:**

   Чтобы получить историю сообщений, используйте:
   ```python
   response = api.get_history(peer_id=12345678, count=20)
   ```

4. **Выполнение кода:**

   Чтобы выполнить небольшой фрагмент кода, подобного JS, на сервере, используйте:
   ```python
   response = api.execute(code="""
        var res0=API.messages.delete({"peer_id":2000000002,"cmids":"152","delete_for_all":1,"spam":0,"group_id":0,"lang":"ru"});
        return [res0];
   """)
   ```

   Вы можете использовать `fork()` для выполнения задач в фоновом режиме и `wait()`, чтобы их подождать.
   Я узнал, что вы можете выполнить только 999 циклов в цикле `while` и 25 API-запросов.

   Вот более сложный пример:
    ```python
   response = api.execute(code="""
        return [  
            wait(fork(  
                API.users.get({    
                    user_ids: 1058611848,    
                    fields: 'photo_100,photo_200,sex,screen_name,first_name_gen,is_nft,animated_avatar,custom_names_for_calls',  
                })
            )),  
            API.calls.getSettings({}),
        ];  
   """)
   ```
