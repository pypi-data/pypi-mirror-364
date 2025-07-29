# coding:utf-8
import csv
import os
from typing import Optional, Dict, List, Union

class langcode_turner:
    """语言代码转换器
    
    支持多种语言代码标准之间的转换，包括：
    - ISO 639-1 (2位代码)
    - ISO 639-2 (3位代码) 
    - ISO 639-3 (3位代码)
    - 各大翻译服务商的语言代码
    
    Example:
        >>> converter = langcode_turner("en")
        >>> converter.iso_639_3
        'eng'
        >>> converter.to_baidu_code()
        'en'
    """
    
    # 类级别的数据缓存
    _data_cache: Optional[List[Dict[str, str]]] = None
    _indices: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None
    
    # 实例属性
    id: str
    iso_639_2b: str
    iso_639_2t: str 
    iso_639_3: str
    iso_639_1: str
    scope: str
    language_type: str
    ref_name: str
    comment: str
    baidu_lang_code: str
    aliyun_lang_code: str
    deepl_lang_code: str
    tencent_lang_code: str
    huawei_lang_code: str
    arc_lang_code: str
    ids_code: str

    @classmethod
    def _load_data(cls) -> List[Dict[str, str]]:
        """加载和缓存CSV数据"""
        if cls._data_cache is None:
            # 从包资源加载CSV文件
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'langcode.csv')
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                cls._data_cache = list(reader)
        return cls._data_cache
    
    @classmethod
    def _build_indices(cls) -> Dict[str, Dict[str, Dict[str, str]]]:
        """构建索引以提高查找性能"""
        if cls._indices is None:
            data = cls._load_data()
            cls._indices = {
                "iso_639_1": {row["iso_639_1"]: row for row in data if row.get("iso_639_1")},
                "iso_639_3": {row["iso_639_3"]: row for row in data if row.get("iso_639_3")},
                "iso_639_2b": {row["iso_639_2b"]: row for row in data if row.get("iso_639_2b")},
                "iso_639_2t": {row["iso_639_2t"]: row for row in data if row.get("iso_639_2t")},
                "ref_name": {row["ref_name"].lower(): row for row in data if row.get("ref_name")},
            }
        return cls._indices
    
    def _detect_code_type(self, langcode: str) -> str:
        """自动检测语言代码类型"""
        if len(langcode) == 2:
            return "iso_639_1"
        elif len(langcode) == 3:
            return "iso_639_3"
        else:
            return "ref_name"

    def __init__(self, langcode: str, code_type: Optional[str] = None):
        """初始化语言代码转换器
        
        Args:
            langcode: 语言代码
            code_type: 代码类型，如果为None则自动检测
            
        Raises:
            ValueError: 当语言代码未找到时
        """
        if not langcode:
            raise ValueError("langcode cannot be empty")
        
        # 自动检测代码类型
        if code_type is None:
            code_type = self._detect_code_type(langcode)
        
        # 使用索引快速查找
        indices = self._build_indices()
        
        row = None
        if code_type in indices:
            if code_type == "ref_name":
                row = indices[code_type].get(langcode.lower())
            else:
                row = indices[code_type].get(langcode)
        
        if row is None:
            raise ValueError(f"Language code '{langcode}' not found")
        
        self._write_in(row)
    
    def _write_in(self, row: Dict[str, str]) -> None:
        """从数据行填充实例属性"""
        self.id = row["iso_639_3"]
        self.iso_639_2b = row["iso_639_2b"] or ""
        self.iso_639_2t = row["iso_639_2t"] or ""
        self.iso_639_3 = row["iso_639_3"]
        self.iso_639_1 = row["iso_639_1"] or ""
        self.scope = row["scope"]
        self.language_type = row["language_type"]
        self.ref_name = row["ref_name"]
        self.comment = row["Comment"] or ""
        self.baidu_lang_code = row["baidu_code"] or ""
        self.aliyun_lang_code = row["aliyun_code"] or ""
        self.deepl_lang_code = row["deepl_code"] or ""
        self.tencent_lang_code = row["tencent_code"] or ""
        self.huawei_lang_code = row["huawei_code"] or ""
        self.arc_lang_code = row["arc_code"] or ""
        self.ids_code = row["ids_code"] or ""
    
    # 便捷的转换方法
    def to_iso_639_1(self) -> str:
        """获取 ISO 639-1 代码"""
        if not self.iso_639_1:
            raise ValueError("ISO 639-1 code not available for this language")
        return self.iso_639_1

    def to_iso_639_3(self) -> str:
        """获取 ISO 639-3 代码"""
        return self.iso_639_3
    
    def to_iso_639_2b(self) -> str:
        """获取 ISO 639-2B 代码"""
        if not self.iso_639_2b:
            raise ValueError("ISO 639-2B code not available for this language")
        return self.iso_639_2b
    
    def to_iso_639_2t(self) -> str:
        """获取 ISO 639-2T 代码"""
        if not self.iso_639_2t:
            raise ValueError("ISO 639-2T code not available for this language")
        return self.iso_639_2t

    def to_baidu_code(self) -> str:
        """获取百度翻译语言代码"""
        if not self.baidu_lang_code:
            raise ValueError("Baidu language code not available for this language")
        return self.baidu_lang_code
    
    def to_aliyun_code(self) -> str:
        """获取阿里云翻译语言代码"""
        if not self.aliyun_lang_code:
            raise ValueError("Aliyun language code not available for this language")
        return self.aliyun_lang_code
    
    def to_deepl_code(self) -> str:
        """获取DeepL翻译语言代码"""
        if not self.deepl_lang_code:
            raise ValueError("DeepL language code not available for this language")
        return self.deepl_lang_code
    
    def to_tencent_code(self) -> str:
        """获取腾讯翻译语言代码"""
        if not self.tencent_lang_code:
            raise ValueError("Tencent language code not available for this language")
        return self.tencent_lang_code
    
    def to_huawei_code(self) -> str:
        """获取华为翻译语言代码"""
        if not self.huawei_lang_code:
            raise ValueError("Huawei language code not available for this language")
        return self.huawei_lang_code
    
    def to_arc_code(self) -> str:
        """获取ARC翻译语言代码"""
        if not self.arc_lang_code:
            raise ValueError("ARC language code not available for this language")
        return self.arc_lang_code
    
    def to_ids_code(self) -> str:
        """获取IDS语言代码"""
        if not self.ids_code:
            raise ValueError("IDS language code not available for this language")
        return self.ids_code

    def wordnet(self) -> str:
        """获取WordNet语言代码"""
        if self.id == "zho":
            return "cmn-Hans"
        return self.iso_639_1
    
    @classmethod
    def convert(cls, langcode: str, from_type: Optional[str] = None, to_type: str = "iso_639_3") -> str:
        """静态方法，直接转换语言代码
        
        Args:
            langcode: 输入的语言代码
            from_type: 输入代码类型，如果为None则自动检测
            to_type: 目标代码类型
            
        Returns:
            转换后的语言代码
            
        Example:
            >>> langcode_turner.convert("en", to_type="iso_639_3")
            'eng'
        """
        converter = cls(langcode, from_type)
        method_name = f"to_{to_type}"
        if hasattr(converter, method_name):
            return getattr(converter, method_name)()
        else:
            # 直接返回属性值
            if hasattr(converter, to_type):
                value = getattr(converter, to_type)
                if value:
                    return value
                else:
                    raise ValueError(f"{to_type} not available for this language")
            else:
                raise ValueError(f"Unknown target type: {to_type}")
    
    @classmethod
    def get_all_languages(cls) -> List[Dict[str, str]]:
        """获取所有支持的语言列表"""
        return cls._load_data()
    
    @classmethod
    def search_languages(cls, query: str) -> List[Dict[str, str]]:
        """根据语言名称搜索语言
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的语言列表
        """
        data = cls._load_data()
        query_lower = query.lower()
        return [row for row in data if query_lower in row.get("ref_name", "").lower()]