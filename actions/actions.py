from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import typing
from typing import Dict, Text, Any, List

from neo4j import GraphDatabase
from rasa_sdk.events import SlotSet

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=False)

def get_product_rel(tx, product,r_type):
    #获得产品product的关系
    query = ("MATCH (:product {name: $product})-[:"+r_type+"]->(items:item)"
        "RETURN items")
    result = tx.run(query,product=product,r_type=r_type)
    return [row.data()["items"]["name"] for row in result]


class ActionUtterProductItems(Action):
    #获得产品解读项
    def name(self) -> Text:
        return "action_utter_product_items"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #初始化product
        product = None
        try:
            #在句子中查找是否有产品实体
            product = next(tracker.get_latest_entity_values("product"))  
        except:
            #在上下文slot中查找是否有产品实体
            product = tracker.get_slot("product")
        finally:
            #若都没有则反问
            if product is None:
                dispatcher.utter_message(text="您想问什么产品的解读项？")
                return []
        r_type = "解读"
        with driver.session() as session:
            res = session.read_transaction(get_product_rel, product,r_type)
            dispatcher.utter_message(text=f"{product}的解读项共有{len(res)}项，分别是：{res[:100]}")
        return [SlotSet("product",product)]