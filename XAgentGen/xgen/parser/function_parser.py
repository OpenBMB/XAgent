from pydantic import BaseModel, create_model,Field,validator
from pydantic.fields import ModelField
from typing import Any, List, Optional,Dict,Union
from enum import Enum
import json
import copy
from outlines.text.json_schema import build_regex_from_object
import xgen.models as models
import xgen.text.generate as generate
import torch
import math

# json schema -> python type
type2type = \
        {
                "string":str,
                "str":str,

                "integer":int,
                "int":int,
                "float":float,
                "number":int,

                "array":list,
                "list":list,

                "object":dict,

                "boolean":bool,
                "bool":bool,

                "null":None,
                "none":None
        }

class FunctionParser:

        def __init__(self) -> None:
                self.functionCallModels = []
                self.regex_strs = []
        
        @classmethod
        def create_total_model(cls):
                class TotalModel(BaseModel):
                        pass
                return TotalModel

        @classmethod
        def create_function_call_model(cls):
                class FunctionCallModel(BaseModel):
                        name:str
                return FunctionCallModel
        
        @classmethod
        def add_property(cls,model, prop_name, prop_type, required, default=None, constrain=None,multi_type = False):
                field_info = model.__fields__
                field_info[prop_name] = ModelField(name=prop_name,type_=prop_type,class_validators={},model_config=model.__config__,required=required,default=default)
                if constrain is not None:
                        field_info[prop_name].field_info.ge = constrain.get('minimum',None)
                        field_info[prop_name].field_info.le = constrain.get('maximum',None)
                        field_info[prop_name].field_info.min_length = constrain.get('minLength',None)
                        field_info[prop_name].field_info.max_length = constrain.get('maxLength',None)
                        field_info[prop_name].field_info.regex = constrain.get('regex',None)
                
                setattr(model, prop_name, field_info)

                if required:
                        setattr(model, f"validate_{prop_name}", validator(prop_name, pre=True, allow_reuse=True)(lambda v: v))
                
                model.__fields__ = field_info

                return model
        
        @classmethod
        def pre_process(cls,prop:Dict[str,Any]):
                new_prop = prop
                if type2type.get(prop["type"],"other type") == list:
                        item_type = type2type[prop["items"]["type"]]
                        if item_type == int:
                                new_prop["type"] = "List[int]"
                        elif item_type == str:
                                new_prop["type"] = "List[str]"
                        elif item_type == bool:
                                new_prop["type"] = "List[bool]"
                        elif item_type == None:
                                new_prop["type"] = "List[null]"

                return new_prop
        
        @classmethod
        def create_list_item_model(cls,prop_json:Dict[str,Any],property_name:str)->Union[BaseModel,str]:
                """
                @param: prop: the property which is a array
                @param: prop_name: the name of array property
                @param: object_model: do the inplace replace for pydantic model
                @return: the pydantic model inherited from BaseModel or a str which describe the List[type]
                """
                item = None
                property_json = cls.pre_process(prop_json)
                if property_json["items"].get("type","no type") == "object":
                        item = cls.create_object_model(property_json["items"],property_name+"_item")
                elif property_json["items"].get("type","no type") == "array":
                        item = cls.create_list_item_model(property_json["items"],property_name+"_arrayItem")
                        item = List[item]
                else:
                        item = type2type.get(property_json["items"]["type"],str)
                return item
        @classmethod
        def create_multi_types(cls,property_name:str,type_list:List[Any])->List[Any]:
                """
                @param: type_list: a list of types of prop
                @return: the list of available type(to be union later)
                """
                new_type_list = []
                for i,tp in enumerate(type_list):
                        if not isinstance(tp,dict):
                                new_type_list.append(type2type.get(tp,str))
                        elif "type" not in tp.keys():
                                continue
                        elif tp["type"] == "object":
                                object_type = cls.create_object_model(tp,property_name + f"_{i}_type_object") 
                                new_type_list.append(object_type)
                        elif tp["type"] == "array":
                                array_type = cls.create_list_item_model(tp,property_name + f"_{i}_type_array")
                                new_type_list.append(List[array_type])

                return new_type_list        


        @classmethod
        def create_object_model(cls,object_item:Dict[str,Any],object_name:str,object_model:BaseModel=None)->BaseModel:
                """
                @param: object_item: the item which is a object(function[parameters]、property、extra_argument[parameters])
                @param: object_name: the name of object item(for property loc)
                @return: the object model inherited from BaseModel
                """
                if object_model is None:
                        object_model = create_model(object_name,__base__=BaseModel)
                assert "properties" in object_item.keys()

                properties = object_item["properties"]
                for property_name in properties.keys():
                        property_json = properties[property_name]

                        if isinstance(property_json["type"],list):
                                multi_type = cls.create_multi_types(property_name,property_json["type"])
                                if len(multi_type) > 1:
                                        multi_type = Union[tuple(multi_type)] # type: ignore
                                if "required" in object_item.keys():                          
                                        if property_name not in object_item["required"]:
                                                if "default" in property_json.keys():
                                                        object_model = cls.add_property(object_model,property_name,multi_type,required=False,default=property_json["default"])
                                                else: 
                                                        object_model = cls.add_property(object_model,property_name,multi_type,required=False)
                                        else:
                                                object_model = cls.add_property(object_model,property_name,multi_type,required=True,default=None)

                                else:
                                        if "default" in properties[property_name].keys():
                                                object_model = cls.add_property(object_model,property_name,multi_type,required=False,default=property_json["default"])
                                        else:
                                                object_model=  cls.add_property(object_model,property_name,multi_type,required=True)
                        elif "enum" in property_json.keys():
                                enum_name = property_name
                                enum_values = {value: value for value in property_json['enum']}
                                enumModel = Enum(enum_name, enum_values)
                                if "required" in object_item.keys():
                                        if property_name not in object_item["required"]:
                                                if "default" in property_json.keys():
                                                        object_model = cls.add_property(object_model,enum_name,enumModel,required=False,default=property_json["default"])
                                                else:
                                                        object_model = cls.add_property(object_model,enum_name,enumModel,required=False)

                                        else:
                                                object_model = cls.add_property(object_model,enum_name,enumModel,required=True)

                                else:
                                        if "default" in property_json.keys():
                                                object_model = cls.add_property(object_model,enum_name,enumModel,required=False,default=property_json["default"])
                                        else:
                                                object_model = cls.add_property(object_model,enum_name,enumModel,required=True)
                        elif property_json["type"] == "array":
                                item = cls.create_list_item_model(property_json,property_name)
                                if item is not None:
                                        if "required" in object_item.keys():
                                                if property_name not in object_item["required"]:
                                                        if "default" in property_json.keys():
                                                                object_model = cls.add_property(object_model,property_name,List[item],required=False,default=property_json["default"])
                                                        else:
                                                                object_model = cls.add_property(object_model,property_name,List[item],required=False)
                                                else:
                                                        object_model = cls.add_property(object_model,property_name,List[item],required=True)
                                        else:
                                                if "default" in property_json.keys():
                                                        object_model = cls.add_property(object_model,property_name,List[item],required=False,default=property_json["default"])
                                                else:
                                                        object_model = cls.add_property(object_model,property_name,List[item],required=True)

                        elif property_json["type"] == "object" and "properties" in property_json.keys():
                                object_property_model = cls.create_object_model(property_json,property_name)
                                if "required" in object_item.keys():
                                        if property_name not in object_item["required"]:
                                                if "default" in property_json.keys():
                                                        object_model = cls.add_property(object_model,property_name,object_property_model,required=False,default=property_json["default"])
                                                else:
                                                        object_model = cls.add_property(object_model,property_name,object_property_model,required=False)
                                        else:
                                                object_model = cls.add_property(object_model,property_name,object_property_model,required=True)
                                else:
                                        if "default" in property_json.keys():
                                                object_model = cls.add_property(object_model,property_name,object_property_model,required=False,default=property_json["default"])
                                        else:
                                                object_model = cls.add_property(object_model,property_name,object_property_model,required=True)

                        else:   
                                constrain = \
                                {
                                        "maxLength":property_json.get("maxLength",None),
                                        "minLength":property_json.get("minLength",None),
                                        "maximum":property_json.get("maximum",None),
                                        "minimum":property_json.get("minimum",None)        
                                }
                                if "required" in object_item.keys():                          
                                        if property_name not in object_item["required"]:
                                                if "default" in property_json.keys():
                                                        object_model = cls.add_property(object_model,property_name,type2type.get(property_json["type"],str),required=False,default=property_json["default"],constrain=constrain)
                                                else:
                                                        object_model = cls.add_property(object_model,property_name,type2type.get(property_json["type"],str),required=False,constrain=constrain)
                                        else:
                                                object_model = cls.add_property(object_model,property_name,type2type.get(property_json["type"],str),required=True,default=None,constrain=constrain)

                                else:
                                        if "default" in properties[property_name].keys():
                                                object_model = cls.add_property(object_model,property_name,type2type.get(property_json["type"],str),required=False,default=property_json["default"],constrain=constrain)
                                        else:
                                                object_model=  cls.add_property(object_model,property_name,type2type.get(property_json["type"],str),required=True,constrain=constrain)

                return object_model

        @classmethod
        def add_function_model(cls,extra_arguments_json:Dict[str,Any],function_json:Dict[str,Any]=None):
                """
                @param: function: the single function to generate a pydantic model
                @param: extra_arguments: the extra arguments
                """
                extra_arguments = copy.deepcopy(extra_arguments_json)
                extra_argumentModel = None
                if extra_arguments is not None and "properties" in extra_arguments.keys():  
                        extra_argumentModel = cls.create_object_model(extra_arguments,"ExtraArgumentModel",extra_argumentModel)
                
                functionCallModel = None
                if function_json is not None:
                        function = copy.deepcopy(function_json)
                        parameters = function["parameters"]
                        if "properties" in parameters.keys():
                                argumentModel = cls.create_object_model(parameters,"ArgumentModel") 

                        functionCallModel = cls.create_function_call_model()
                        functionCallModel = cls.add_property(functionCallModel,"name",str,required=True,constrain={"regex":function["name"]})
                        if argumentModel is not None:
                                functionCallModel = cls.add_property(functionCallModel,"arguments",argumentModel,required=True)
                totalModel = cls.create_total_model()
                if extra_argumentModel is not None:
                        totalModel = cls.add_property(totalModel,"arguments",extra_argumentModel,required=True)
                if functionCallModel is not None:
                        totalModel = cls.add_property(totalModel,"function_call",functionCallModel,required=True)
                return totalModel      
          
        
        def create_all_functions_model(self,extra_arguments:Dict[str,Any]=None,functions:list=None,function_call:Dict[str,Any]=None):
                """
                @param: functions: a list of functions
                @param: extra_argument: a json of extra_arguments
                @param: function_call: a json of function call
                """ 
                self.functionCallModels = []
                if  functions is None or len(functions)==0:
                        self.functionCallModels.append(self.add_function_model(extra_arguments))
                        return
                for function in functions:
                        if function_call is not None and "name" in function_call.keys():
                                if  function_call["name"] == function["name"]:
                                        self.functionCallModels.append(self.add_function_model(extra_arguments,function))
                                        return
                        else:
                                self.functionCallModels.append(self.add_function_model(extra_arguments,function))


        def models_to_regex(self):
                self.regex_strs = []
                for function in self.functionCallModels:
                    if hasattr(function, "model_json_schema"):
                        json_schema = function.model_json_schema()
                    else: 
                        json_schema = function.schema()

                    json_schema = self.post_process(json_schema)
                    schema = json.dumps(json_schema)
                    self.regex_strs.append(build_regex_from_object(schema))
                return self.regex_strs


        def context_ids_next_ids(self,context_ids:List[int]):
                """
                @param: context_ids: the ids of generated tokens (list[list[int]])
                @return: valid_ids: the valid ids of next token (list[list[int]])
                """
                # you should empty the pstates every times except you input all context in order)
                self.generator.pstates = []
                import traceback
                logits = torch.ones(len(self.model.tokenizer.vocabulary)).to(self.model.device)
                # masked_logits 
                try:
                        masked_logits = self.generator.create_proposal(torch.tensor([context_ids]).to(self.model.device), logits)
                        # valid indexes
                        non_inf_indices = torch.nonzero(masked_logits != -math.inf).squeeze(dim=1)
                        non_inf_indices = non_inf_indices[:,1]
                        non_inf_indices = non_inf_indices.tolist()
                except Exception as e:
                        print("no available path")
                        non_inf_indices = []
                return non_inf_indices


        def post_process(self,schema):   
                com_schema = schema
                if "definitions" in com_schema.keys():
                        for prop in com_schema["definitions"].keys():
                                if "type" not in com_schema["definitions"][prop].keys():
                                        com_schema["definitions"][prop]["type"]="string"
                
                return com_schema

        def create_generator(self,model:models.XTransformers,function_info:Dict[str,Any],generate_params:Dict = {}):
                """
                @param: model: the transformer model
                @param: functions: a list of functions
                @param: extra_argument: a json of extra_arguments
                @param: function_call: a json of function call name
                @param: generate_params: a dict of inference constraint arguments
                @return: create a generator for guided generate
                """    
                extra_arguments = function_info.get("arguments",None)
                functions = function_info.get("functions",None)
                function_call = function_info.get("function_call",None)
                self.create_all_functions_model(extra_arguments,functions,function_call) 
                regex_list = self.models_to_regex()
                self.model = model
                # temperature and so on
                self.model.add_logits_processor(generate_params)
                self.generator = generate.multi_regex(self.model, regex_list,generate_params.get("max_tokens"))
                return self.generator
        
        def check(self,call_info:str):
                """
                @param: function: the dynamic BaseModel generated for specified function
                """
                try:
                        call_info_json = json.loads(call_info)
                except Exception:
                        return False
                if "name" not in call_info_json.keys():
                        return False
                if "arguments" not in call_info_json.keys():
                        return False
                try:
                        self.functionCallModel.model_validate_json(call_info)
                except Exception:
                        return False
                return True
        

