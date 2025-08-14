"""
애플리케이션 설정 관리 모듈
새로고침 간격 등의 사용자 설정을 JSON 파일로 저장/로드합니다.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ConfigManager:
    """애플리케이션 설정 관리 클래스"""
    
    def __init__(self, config_file_path: str = None):
        """
        설정 관리자 초기화
        
        Args:
            config_file_path: 설정 파일 경로 (기본값: config/settings.json)
        """
        if config_file_path is None:
            # 현재 스크립트 위치 기준으로 설정 파일 경로 결정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.config_file_path = os.path.join(parent_dir, "config", "settings.json")
        else:
            self.config_file_path = config_file_path
            
        # 설정 파일 디렉토리 생성
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
        
        # 기본 설정값
        self.default_settings = {
            "refresh_intervals": {
                "dsct_sensor": 5,
                "aircon_sensor": 5
            },
            "csv_cleanup": {
                "enabled": True,
                "max_files_per_type": 20  # 각 타입(DSCT, AIRCON)당 최대 20개 파일
            },
            "last_updated": None
        }
        
        # 설정 로드
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """설정 파일에서 설정 로드"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 기본값과 병합 (누락된 키 보완)
                merged_settings = self._merge_with_defaults(settings)
                return merged_settings
            else:
                # 설정 파일이 없으면 기본값으로 생성
                self._save_settings(self.default_settings)
                return self.default_settings.copy()
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"설정 파일 로드 중 오류 발생: {e}")
            print("기본 설정값을 사용합니다.")
            # 오류 발생 시 기본값 사용 및 저장
            self._save_settings(self.default_settings)
            return self.default_settings.copy()
            
    def _merge_with_defaults(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """로드된 설정과 기본값을 병합"""
        merged = self.default_settings.copy()
        
        # refresh_intervals 병합
        if "refresh_intervals" in loaded_settings and isinstance(loaded_settings["refresh_intervals"], dict):
            merged["refresh_intervals"].update(loaded_settings["refresh_intervals"])
            
        # 기타 설정값 병합
        for key, value in loaded_settings.items():
            if key != "refresh_intervals":
                merged[key] = value
                
        return merged
        
    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """설정을 파일에 저장"""
        try:
            # 저장할 설정의 복사본 생성 (원본 수정 방지)
            import copy
            save_data = copy.deepcopy(settings)
            
            # 마지막 업데이트 시간 추가
            save_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
            
        except IOError as e:
            print(f"설정 파일 저장 중 오류 발생: {e}")
            return False
            
    def load_refresh_interval(self, sensor_type: str) -> int:
        """
        특정 센서 타입의 새로고침 간격 로드
        
        Args:
            sensor_type: 'dsct_sensor' 또는 'aircon_sensor'
            
        Returns:
            새로고침 간격 (초)
        """
        try:
            interval = self.settings["refresh_intervals"].get(sensor_type, 5)
            # 유효성 검증 (1~360초)
            if not isinstance(interval, int) or interval < 1 or interval > 360:
                print(f"유효하지 않은 간격값: {interval}. 기본값 5초 사용.")
                return 5
            return interval
        except (KeyError, TypeError):
            print(f"설정 로드 오류. 기본값 5초 사용.")
            return 5
            
    def save_refresh_interval(self, sensor_type: str, interval: int) -> bool:
        """
        특정 센서 타입의 새로고침 간격 저장
        
        Args:
            sensor_type: 'dsct_sensor' 또는 'aircon_sensor'
            interval: 새로고침 간격 (초, 1~360)
            
        Returns:
            저장 성공 여부
        """
        # 유효성 검증
        if not isinstance(interval, int) or interval < 1 or interval > 360:
            print(f"유효하지 않은 간격값: {interval}. 저장하지 않습니다.")
            return False
            
        if sensor_type not in ["dsct_sensor", "aircon_sensor"]:
            print(f"유효하지 않은 센서 타입: {sensor_type}")
            return False
            
        try:
            # 현재 설정 업데이트
            self.settings["refresh_intervals"][sensor_type] = interval
            
            # 파일에 저장
            success = self._save_settings(self.settings)
            
            if success:
                print(f"{sensor_type} 새로고침 간격을 {interval}초로 저장했습니다.")
            
            return success
            
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")
            return False
            
    def get_all_refresh_intervals(self) -> Dict[str, int]:
        """모든 센서의 새로고침 간격 반환"""
        return self.settings["refresh_intervals"].copy()
        
    def get_last_updated(self) -> Optional[str]:
        """마지막 업데이트 시간 반환"""
        return self.settings.get("last_updated")
        
    def reset_to_defaults(self) -> bool:
        """설정을 기본값으로 초기화"""
        try:
            # 깊은 복사로 기본값 복사
            import copy
            self.settings = copy.deepcopy(self.default_settings)
            success = self._save_settings(self.settings)
            
            if success:
                print("설정이 기본값으로 초기화되었습니다.")
                # 파일 저장 후 다시 로드하여 동기화
                self.settings = self._load_settings()
                
            return success
            
        except Exception as e:
            print(f"설정 초기화 중 오류 발생: {e}")
            return False


# 전역 설정 관리자 인스턴스
_config_manager = None

def get_config_manager() -> ConfigManager:
    """전역 설정 관리자 인스턴스 반환 (싱글톤 패턴)"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager