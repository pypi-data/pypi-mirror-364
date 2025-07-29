from ep_sdk_4pd.ep_data import EpData
from ep_sdk_4pd.ep_system import EpSystem

target_date = EpSystem.init_env("inner").get_system_date()  # 应该需要增加一天表示预测第二天
plant_forecast_power= EpData.get_predict_data(scope="plant", is_test=True)
print(plant_forecast_power)
plant_forecast = [float(item['predicted_power']) for item in plant_forecast_power]
print(plant_forecast)