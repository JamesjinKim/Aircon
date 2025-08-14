"""
CSV 파일 자동 정리 유틸리티
- 개수 기반 정리: 최대 파일 개수 제한
- 날짜 기반 정리: 보관 기간 제한
- 크기 기반 정리: 총 크기 제한
"""

import os
import glob
from datetime import datetime, timedelta
from typing import List, Tuple


class CSVCleaner:
    """CSV 파일 자동 정리 클래스"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def cleanup_by_count(self, max_files: int = 30, pattern: str = "*.csv") -> List[str]:
        """
        개수 기반 파일 정리
        
        Args:
            max_files: 보관할 최대 파일 개수
            pattern: 파일 패턴 (예: "DSCT_*.csv", "AIRCON_*.csv")
            
        Returns:
            삭제된 파일 목록
        """
        deleted_files = []
        
        if not os.path.exists(self.data_dir):
            return deleted_files
            
        # 패턴에 맞는 모든 파일 찾기
        search_pattern = os.path.join(self.data_dir, pattern)
        csv_files = glob.glob(search_pattern)
        
        if len(csv_files) <= max_files:
            return deleted_files
            
        # 파일을 수정 시간순으로 정렬 (오래된 것부터)
        csv_files.sort(key=lambda f: os.path.getmtime(f))
        
        # 초과하는 파일들 삭제
        files_to_delete = csv_files[:-max_files]
        
        for file_path in files_to_delete:
            try:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_files.append(filename)
                print(f"[CSV_CLEANER] 파일 삭제: {filename} ({file_size} bytes)")
            except Exception as e:
                print(f"[CSV_CLEANER] 파일 삭제 실패: {file_path}, 오류: {e}")
                
        return deleted_files
    
    def cleanup_by_age(self, max_days: int = 30, pattern: str = "*.csv") -> List[str]:
        """
        날짜 기반 파일 정리
        
        Args:
            max_days: 보관할 최대 일수
            pattern: 파일 패턴
            
        Returns:
            삭제된 파일 목록
        """
        deleted_files = []
        
        if not os.path.exists(self.data_dir):
            return deleted_files
            
        cutoff_time = datetime.now() - timedelta(days=max_days)
        
        # 패턴에 맞는 모든 파일 찾기
        search_pattern = os.path.join(self.data_dir, pattern)
        csv_files = glob.glob(search_pattern)
        
        for file_path in csv_files:
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    filename = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_files.append(filename)
                    days_old = (datetime.now() - file_mtime).days
                    print(f"[CSV_CLEANER] 오래된 파일 삭제: {filename} ({days_old}일 전, {file_size} bytes)")
                    
            except Exception as e:
                print(f"[CSV_CLEANER] 파일 삭제 실패: {file_path}, 오류: {e}")
                
        return deleted_files
    
    def cleanup_by_size(self, max_size_mb: int = 100, pattern: str = "*.csv") -> List[str]:
        """
        크기 기반 파일 정리
        
        Args:
            max_size_mb: 최대 총 크기 (MB)
            pattern: 파일 패턴
            
        Returns:
            삭제된 파일 목록
        """
        deleted_files = []
        
        if not os.path.exists(self.data_dir):
            return deleted_files
            
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # 패턴에 맞는 모든 파일 찾기
        search_pattern = os.path.join(self.data_dir, pattern)
        csv_files = glob.glob(search_pattern)
        
        # 파일을 수정 시간순으로 정렬 (오래된 것부터)
        csv_files.sort(key=lambda f: os.path.getmtime(f))
        
        # 현재 총 크기 계산
        total_size = sum(os.path.getsize(f) for f in csv_files)
        
        if total_size <= max_size_bytes:
            return deleted_files
            
        # 크기가 초과되면 오래된 파일부터 삭제
        for file_path in csv_files:
            if total_size <= max_size_bytes:
                break
                
            try:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_files.append(filename)
                total_size -= file_size
                print(f"[CSV_CLEANER] 크기 제한으로 파일 삭제: {filename} ({file_size} bytes)")
                
            except Exception as e:
                print(f"[CSV_CLEANER] 파일 삭제 실패: {file_path}, 오류: {e}")
                
        return deleted_files
    
    def auto_cleanup(self, max_files: int = 20) -> Tuple[List[str], List[str]]:
        """
        자동 정리 (DSCT와 AIRCON 파일 각각 최대 20개 유지)
        
        Args:
            max_files: 각 타입당 최대 파일 개수 (기본값: 20)
            
        Returns:
            (DSCT 삭제 파일 목록, AIRCON 삭제 파일 목록)
        """
        print(f"[CSV_CLEANER] 자동 정리 시작 - 각 타입당 최대 {max_files}개 파일 유지")
        
        # DSCT 파일 정리 (개수 기반만)
        dsct_deleted = self.cleanup_by_count(max_files, "DSCT_*.csv")
        
        # AIRCON 파일 정리 (개수 기반만)
        aircon_deleted = self.cleanup_by_count(max_files, "AIRCON_*.csv")
        
        total_deleted = len(dsct_deleted) + len(aircon_deleted)
        if total_deleted > 0:
            print(f"[CSV_CLEANER] 정리 완료 - DSCT: {len(dsct_deleted)}개, AIRCON: {len(aircon_deleted)}개 삭제")
        else:
            print("[CSV_CLEANER] 정리할 파일 없음")
            
        return dsct_deleted, aircon_deleted
    
    def get_stats(self) -> dict:
        """데이터 폴더 통계 정보 반환"""
        if not os.path.exists(self.data_dir):
            return {"total_files": 0, "total_size_mb": 0, "dsct_files": 0, "aircon_files": 0}
            
        dsct_files = glob.glob(os.path.join(self.data_dir, "DSCT_*.csv"))
        aircon_files = glob.glob(os.path.join(self.data_dir, "AIRCON_*.csv"))
        all_files = dsct_files + aircon_files
        
        total_size = sum(os.path.getsize(f) for f in all_files)
        
        return {
            "total_files": len(all_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "dsct_files": len(dsct_files),
            "aircon_files": len(aircon_files)
        }