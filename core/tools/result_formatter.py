"""Format kết quả truy vấn thành output dễ hiểu cho người dùng"""
import json
from typing import Any, List, Dict

def format_results(results: List[Dict], query: str, row_limit: int = 10) -> Dict[str, Any]:
    """
    Format kết quả từ database thành một output dễ đọc.
    
    Args:
        results: Danh sách dicts từ query
        query: Câu hỏi gốc của người dùng
        row_limit: Giới hạn số dòng hiển thị
    
    Returns:
        Dict với formatted output
    """
    
    if not results:
        return {
            "status": "success",
            "total_rows": 0,
            "message": "Không tìm thấy dữ liệu phù hợp với yêu cầu.",
            "data": []
        }
    
    # Giới hạn kết quả
    display_results = results[:row_limit]
    total_rows = len(results)
    
    # Tạo summary dựa trên loại query
    summary = _generate_summary(display_results, query, total_rows)
    
    # Định dạng dữ liệu
    formatted_data = []
    for row in display_results:
        formatted_row = {k: (v if not isinstance(v, (dict, list)) else json.dumps(v)) 
                        for k, v in row.items()}
        formatted_data.append(formatted_row)
    
    return {
        "status": "success",
        "total_rows": total_rows,
        "displayed_rows": len(formatted_data),
        "summary": summary,
        "data": formatted_data,
        "note": f"Hiển thị {len(formatted_data)} / {total_rows} kết quả" if total_rows > row_limit else None
    }

def _generate_summary(results: List[Dict], query: str, total_rows: int) -> str:
    """Tạo summary mô tả kết quả theo yêu cầu người dùng"""
    
    if not results:
        return "Không có dữ liệu."
    
    # Phát hiện loại query từ từ khoá
    query_lower = query.lower()
    
    # Query về tổng/thống kê
    if any(word in query_lower for word in ['tổng', 'sum', 'cộng', 'total', 'số lượng', 'count']):
        if len(results) == 1:
            # Trả kết quả số duy nhất
            first_val = next(iter(results[0].values()))
            return f"Kết quả: {first_val}"
        return f"Tìm thấy {total_rows} kết quả tương ứng."
    
    # Query về danh sách/đối tượng
    if any(word in query_lower for word in ['danh sách', 'list', 'những', 'tất cả']):
        return f"Tìm thấy {total_rows} mục phù hợp với yêu cầu của bạn."
    
    # Query về tìm kiếm/lọc
    if any(word in query_lower for word in ['tìm', 'search', 'filter', 'lọc', 'nào']):
        return f"Tìm thấy {total_rows} bản ghi phù hợp."
    
    # Query về top/xếp hạng
    if any(word in query_lower for word in ['top', 'cao nhất', 'thấp nhất', 'hơn', 'nhanh nhất']):
        return f"Hiển thị {len(results)} kết quả xếp hạng hàng đầu."
    
    # Default
    return f"Tìm thấy {total_rows} kết quả."

def create_answer(query: str, formatted_results: Dict[str, Any], sql: str = None) -> str:
    """Tạo câu trả lời tự nhiên cho người dùng"""
    
    summary = formatted_results.get("summary", "")
    total = formatted_results.get("total_rows", 0)
    
    answer = f"**Kết quả truy vấn của bạn:**\n\n{summary}"
    
    if total == 0:
        answer = "Xin lỗi, hệ thống không tìm thấy dữ liệu phù hợp với yêu cầu của bạn."
    elif total == 1:
        answer = f"Tìm thấy 1 kết quả: {summary}"
    elif total > 1:
        answer = f"Tìm thấy {total} kết quả: {summary}"
    
    return answer

if __name__ == "__main__":
    # Test
    test_results = [
        {"account_name": "ABC Corp", "revenue": 1000000, "industry": "Finance"},
        {"account_name": "XYZ Ltd", "revenue": 2000000, "industry": "Finance"},
    ]
    formatted = format_results(test_results, "Tìm các công ty ngành Finance")
    print(json.dumps(formatted, indent=2, ensure_ascii=False))
