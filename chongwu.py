import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

class PetAdoptionPlatform:
    def __init__(self):
        self.data_file = "pet_adoption_data.json"
        self.data = self._load_data()
        
    def _load_data(self):
        """加载或初始化数据文件"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                st.error("数据文件损坏，将创建新文件")
        return {"pets": [], "adopters": [], "adoptions": []}
    
    def _save_data(self):
        """保存数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_pet(self, name, species, breed, age, gender, size, temperament, description):
        """添加待领养宠物"""
        pet = {
            "id": len(self.data["pets"]) + 1,
            "name": name,
            "species": species,
            "breed": breed,
            "age": age,
            "gender": gender,
            "size": size,
            "temperament": temperament,
            "description": description,
            "status": "待领养",
            "adoption_date": None,
            "adopter_id": None
        }
        self.data["pets"].append(pet)
        self._save_data()
        return pet
    
    def register_adopter(self, name, contact, living_situation, experience, preferences):
        """注册领养人"""
        adopter = {
            "id": len(self.data["adopters"]) + 1,
            "name": name,
            "contact": contact,
            "living_situation": living_situation,
            "experience": experience,
            "preferences": preferences
        }
        self.data["adopters"].append(adopter)
        self._save_data()
        return adopter
    
    def match_pets(self, adopter_id):
        """为领养人匹配合适的宠物"""
        adopter = next((a for a in self.data["adopters"] if a["id"] == adopter_id), None)
        if not adopter:
            return []
        
        matched = []
        for pet in self.data["pets"]:
            if pet["status"] != "待领养":
                continue
                
            # 基础匹配：宠物类型和大小
            species_match = not adopter["preferences"].get("species") or pet["species"] in adopter["preferences"]["species"]
            size_match = not adopter["preferences"].get("size") or pet["size"] in adopter["preferences"]["size"]
            
            # 进阶匹配：年龄和性格
            age_group = self._get_age_group(pet["age"])
            age_match = not adopter["preferences"].get("age") or age_group in adopter["preferences"]["age"]
            
            temperament_match = not adopter["preferences"].get("temperament") or any(
                t in adopter["preferences"]["temperament"] for t in pet["temperament"]
            )
            
            # 放宽匹配条件：只要有一项偏好匹配即可
            if species_match and size_match and (age_match or temperament_match):
                matched.append(pet)
        
        return matched
    
    def _get_age_group(self, age):
        """将年龄转换为年龄组"""
        if age < 1:
            return "幼年"
        elif age < 3:
            return "青年"
        elif age < 8:
            return "成年"
        else:
            return "老年"
    
    def adopt_pet(self, adopter_id, pet_id):
        """领养宠物"""
        # 查找领养人
        adopter = next((a for a in self.data["adopters"] if a["id"] == adopter_id), None)
        if not adopter:
            return "领养人不存在"
            
        # 查找宠物
        pet = next((p for p in self.data["pets"] if p["id"] == pet_id), None)
        if not pet:
            return "宠物不存在"
            
        # 检查宠物状态
        if pet["status"] != "待领养":
            return "该宠物已被领养"
        
        # 更新宠物状态
        pet["status"] = "已领养"
        pet["adoption_date"] = datetime.now().strftime("%Y-%m-%d")
        pet["adopter_id"] = adopter_id
        
        # 记录领养信息
        adoption = {
            "id": len(self.data["adoptions"]) + 1,
            "pet_id": pet_id,
            "adopter_id": adopter_id,
            "date": pet["adoption_date"]
        }
        self.data["adoptions"].append(adoption)
        
        # 保存数据
        self._save_data()
        
        return f"成功领养宠物: {pet['name']}"
    
    def list_pets(self, status=None):
        """列出宠物"""
        if status:
            return [p for p in self.data["pets"] if p["status"] == status]
        return self.data["pets"]

# 初始化应用
platform = PetAdoptionPlatform()

# 添加示例数据
if not platform.data["pets"]:
    platform.add_pet(
        "小黄", "狗狗", "金毛", 2, "公", "中大型", ["温顺", "友善", "活泼"], 
        "非常亲人的金毛，喜欢和人互动，适合有耐心的家庭。"
    )
    platform.add_pet(
        "小黑", "猫咪", "英短", 1, "公", "小型", ["独立", "安静", "粘人"], 
        "安静乖巧的英短，喜欢独处但也会撒娇，适合上班族。"
    )
    platform.add_pet(
        "小白", "狗狗", "泰迪", 3, "母", "小型", ["聪明", "活泼", "爱叫"], 
        "聪明活泼的泰迪，需要定期梳理毛发，适合有时间照顾的家庭。"
    )
    platform.add_pet(
        "小花", "猫咪", "布偶", 4, "母", "中型", ["温顺", "粘人", "高贵"], 
        "优雅的布偶猫，性格温顺，喜欢被宠爱，适合有耐心的主人。"
    )
    platform.add_pet(
        "小灰", "猫咪", "美短", 2, "公", "中型", ["活泼", "聪明", "独立"], 
        "精力充沛的美短，喜欢玩耍，适合有活力的家庭。"
    )
    platform.add_pet(
        "小汪", "狗狗", "柯基", 1, "母", "小型", ["友善", "活泼", "固执"], 
        "可爱的柯基，短腿长身，性格开朗，适合喜欢户外活动的家庭。"
    )

# Streamlit应用
st.set_page_config(
    page_title="宠物领养匹配平台",
    page_icon="🐾",
    layout="wide"
)

# 侧边栏
with st.sidebar:
    st.title("🐾 宠物领养匹配平台")
    st.markdown("---")
    
    page = st.radio(
        "选择功能",
        ["首页", "注册领养人", "浏览宠物", "查找匹配宠物"]
    )
    
    st.markdown("---")
    st.info("💡 提示：通过侧边栏选择不同功能")

# 主页面
if page == "首页":
    st.header("欢迎来到宠物领养匹配平台")
    st.write("我们帮助您找到最适合的宠物伙伴，开启幸福的陪伴之旅")
    
    # 统计数据
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("待领养宠物", len(platform.list_pets("待领养")))
    with col2:
        st.metric("已领养宠物", len(platform.list_pets("已领养")))
    with col3:
        st.metric("注册领养人", len(platform.data["adopters"]))
    
    # 数据统计表格
    st.subheader("平台数据统计")
    
    # 宠物统计
    pets = platform.list_pets()
    if pets:
        st.markdown("#### 宠物统计")
        pet_df = pd.DataFrame(pets)
        
        # 按类型统计
        species_counts = pet_df['species'].value_counts().reset_index()
        species_counts.columns = ['宠物类型', '数量']
        st.dataframe(species_counts)
        
        # 按状态统计
        status_counts = pet_df['status'].value_counts().reset_index()
        status_counts.columns = ['状态', '数量']
        st.dataframe(status_counts)
        
        # 按年龄分布
        pet_df['age_group'] = pet_df['age'].apply(lambda x: platform._get_age_group(x))
        age_counts = pet_df['age_group'].value_counts().reset_index()
        age_counts.columns = ['年龄组', '数量']
        st.dataframe(age_counts)
    else:
        st.info("暂无宠物数据")
    
    # 领养统计
    adoptions = platform.data["adoptions"]
    if adoptions:
        st.markdown("#### 领养统计")
        adoption_df = pd.DataFrame(adoptions)
        adoption_df['date'] = pd.to_datetime(adoption_df['date'])
        
        # 按月统计领养数量
        monthly_adoptions = adoption_df['date'].dt.to_period('M').value_counts().sort_index().reset_index()
        monthly_adoptions.columns = ['月份', '领养数']
        st.dataframe(monthly_adoptions)
        
        st.write(f"总领养数: {len(adoptions)}")
    else:
        st.info("暂无领养数据")

elif page == "注册领养人":
    st.header("注册领养人")
    
    with st.form("adopter_registration"):
        name = st.text_input("您的姓名")
        contact = st.text_input("联系方式（电话/邮箱）")
        
        st.subheader("居住情况")
        living_situation = st.selectbox(
            "居住类型",
            ["公寓", "独栋房屋", "合租", "其他"]
        )
        pet_policy = st.selectbox(
            "居住处宠物政策",
            ["允许养宠物", "有限制条件", "不允许养宠物"]
        )
        
        st.subheader("养宠经验")
        experience = st.multiselect(
            "养宠经验",
            ["从未养过", "曾养过宠物", "现在养有宠物", "有专业养宠经验"]
        )
        
        st.subheader("宠物偏好")
        species = st.multiselect(
            "偏好的宠物类型",
            ["狗狗", "猫咪", "其他"]
        )
        size = st.multiselect(
            "偏好的宠物大小",
            ["小型", "中型", "大型", "无所谓"]
        )
        age = st.multiselect(
            "偏好的宠物年龄",
            ["幼年", "青年", "成年", "老年", "无所谓"]
        )
        temperament = st.multiselect(
            "偏好的宠物性格",
            ["温顺", "活泼", "独立", "粘人", "聪明", "友善", "安静"]
        )
        
        preferences = {
            "species": species,
            "size": size,
            "age": age,
            "temperament": temperament
        }
        
        submitted = st.form_submit_button("注册")
        
        if submitted:
            if not name:
                st.error("请输入您的姓名")
            elif not contact:
                st.error("请输入您的联系方式")
            elif not species:
                st.error("请至少选择一种偏好的宠物类型")
            else:
                adopter = platform.register_adopter(name, contact, living_situation, experience, preferences)
                st.success(f"注册成功！您的领养人ID是: {adopter['id']}")
                st.info("请记住您的领养人ID，用于后续操作")

elif page == "浏览宠物":
    st.header("浏览待领养宠物")
    
    pets = platform.list_pets("待领养")
    if not pets:
        st.warning("目前没有待领养的宠物")
    else:
        # 过滤选项
        col1, col2, col3 = st.columns(3)
        with col1:
            species_filter = st.selectbox("按类型筛选", ["全部"] + list({p["species"] for p in pets}))
        with col2:
            size_filter = st.selectbox("按大小筛选", ["全部"] + list({p["size"] for p in pets}))
        with col3:
            age_filter = st.selectbox("按年龄筛选", ["全部"] + ["幼年", "青年", "成年", "老年"])
        
        # 应用过滤
        filtered_pets = pets
        if species_filter != "全部":
            filtered_pets = [p for p in filtered_pets if p["species"] == species_filter]
        if size_filter != "全部":
            filtered_pets = [p for p in filtered_pets if p["size"] == size_filter]
        if age_filter != "全部":
            filtered_pets = [p for p in filtered_pets if platform._get_age_group(p["age"]) == age_filter]
        
        st.write(f"找到 {len(filtered_pets)} 只宠物")
        
        # 显示宠物信息
        for pet in filtered_pets:
            st.subheader(pet["name"])
            st.write(f"**品种**: {pet['breed']}")
            st.write(f"**年龄**: {pet['age']}岁")
            st.write(f"**性别**: {pet['gender']}")
            st.write(f"**体型**: {pet['size']}")
            st.write(f"**性格**: {', '.join(pet['temperament'])}")
            st.write(f"**描述**: {pet['description']}")
            
            if st.button(f"申请领养 - {pet['name']}"):
                with st.form(key=f'adopt_form_{pet["id"]}'):
                    st.write(f"您确定要领养 {pet['name']} 吗？")
                    adopter_id = st.number_input("请输入您的领养人ID", min_value=1, step=1)
                    confirm = st.form_submit_button("确认领养")
                    
                    if confirm:
                        result = platform.adopt_pet(adopter_id, pet["id"])
                        if "成功" in result:
                            st.success(result)
                            # 刷新页面以更新宠物状态
                            st.experimental_rerun()
                        else:
                            st.error(result)

elif page == "查找匹配宠物":
    st.header("查找匹配的宠物")
    
    adopter_id = st.number_input("请输入您的领养人ID", min_value=1, step=1)
    
    if st.button("查找匹配宠物"):
        adopter = next((a for a in platform.data["adopters"] if a["id"] == adopter_id), None)
        if not adopter:
            st.error("领养人不存在，请检查您的领养人ID")
        else:
            st.markdown(f"### 匹配条件：")
            st.markdown(f"- **居住类型**: {adopter['living_situation']}")
            st.markdown(f"- **宠物偏好**:")
            st.markdown(f"  - **类型**: {', '.join(adopter['preferences'].get('species', ['未选择']))}")
            st.markdown(f"  - **大小**: {', '.join(adopter['preferences'].get('size', ['未选择']))}")
            st.markdown(f"  - **年龄**: {', '.join(adopter['preferences'].get('age', ['未选择']))}")
            st.markdown(f"  - **性格**: {', '.join(adopter['preferences'].get('temperament', ['未选择']))}")
            
            matched = platform.match_pets(adopter_id)
            
            if not matched:
                st.warning("没有找到匹配的宠物，您可以尝试以下操作：")
                st.markdown("- 扩大您的宠物类型偏好范围")
                st.markdown("- 增加您对宠物大小、年龄的接受范围")
                st.markdown("- 浏览全部宠物并手动选择感兴趣的宠物")
            else:
                st.success(f"为您找到 {len(matched)} 只匹配的宠物")
                
                for pet in matched:
                    st.subheader(pet["name"])
                    st.write(f"**品种**: {pet['breed']}")
                    st.write(f"**年龄**: {pet['age']}岁")
                    st.write(f"**性别**: {pet['gender']}")
                    st.write(f"**体型**: {pet['size']}")
                    st.write(f"**性格**: {', '.join(pet['temperament'])}")
                    st.write(f"**描述**: {pet['description']}")
                    
                    if st.button(f"申请领养 - {pet['name']}"):
                        with st.form(key=f'adopt_form_{pet["id"]}'):
                            st.write(f"您确定要领养 {pet['name']} 吗？")
                            adopter_id = st.number_input("请输入您的领养人ID", min_value=1, step=1)
                            confirm = st.form_submit_button("确认领养")
                            
                            if confirm:
                                result = platform.adopt_pet(adopter_id, pet["id"])
                                if "成功" in result:
                                    st.success(result)
                                    # 刷新页面以更新宠物状态
                                    st.experimental_rerun()
                                else:
                                    st.error(result)    
