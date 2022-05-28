import json
import logging
from random import randint
from time import sleep

from channels.generic.websocket import WebsocketConsumer

from apps.api import TwitterAPI
from apps.models import Topic, Tweet

from asgiref.sync import async_to_sync

# Get an instance of a logger
logger = logging.getLogger('htv')

class Consumer(WebsocketConsumer):

    def connect(self):
        config = self.scope['path'].strip('/').split('/')
        if config[0] == 'search':
            del config[0]
        label = config[0]
        self.room_name = 'htv-' + label + str(randint(100,999))
        self.room_group_name = 'group_' + self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.scope['groupname'] = self.room_group_name
        # creo un Topic
        topic = Topic(query=label)
        topic.frequency = config[1] if len(config) > 1 else 5
        topic.save()
        # almaceno en sesión datos que necesitaré luego
        self.scope['last_id'] = 1
        self.scope['topic_pk'] = topic.pk
        self.scope["first"] = True

        self.accept()
        logger.debug("Conectado. Nuevo topic: %s" % label)


    def receive(self, text_data):
        if "topic_pk" not in self.scope.keys():
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {'text': json.dumps({'retry': True})}
                }
            )
            return
        topic = Topic.objects.get(pk=self.scope["topic_pk"])
        tw = TwitterAPI()
        data = json.loads(text_data)
        # búscamos nuevos tweets
        if self.scope["first"]:
            logger.debug("Primera búsqueda, 30 tweets")
            tweets = tw.search(topic, self.scope['last_id'], 30)
            self.scope['last_id'] = tweets[len(tweets)-1].twitter_id if tweets else 1
            self.scope["first"] = False
        else:
            tweets = tw.search(topic, self.scope['last_id'], data['count'])
        for tweet in tweets[:10]:
            if tweet.twitter_id > self.scope['last_id']:
                self.scope['last_id'] = tweet.twitter_id
            logger.debug("Enviando tweet ID: %s" % (tweet.twitter_id))
            # mandar tweets
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {'text': json.dumps(tweet.as_json())}
                }
            )
            tweet.show()
            logger.debug("Durmiendo %s segundos" % topic.frequency)
            sleep(topic.frequency)

        if len(tweets) < data['count']:  # si no hay tweet nuevos, repetir pero buscando los mostrados hace más tiempo
            diff = data['count'] - len(tweets)
            for tweet_ret in Tweet.objects.filter(topic=topic).order_by('last_shown')[:diff]:
                logger.debug("Repitiendo tweet ID %s" % tweet_ret.twitter_id)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {'text': json.dumps(tweet_ret.as_json())}
                    }
                )
                tweet_ret.show()
                sleep(topic.frequency)


    def disconnect(self, close_code):
        logger.debug("Se desconectó el cliente.")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))        
