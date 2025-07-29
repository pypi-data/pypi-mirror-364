"""Checklist component module

Provides ChecklistWidget class for creating task lists, todo items, or checklists in emails.
Supports multiple states, theme colors, and style configurations.
"""

from typing import Any

from email_widget.core.base import BaseWidget
from email_widget.core.enums import StatusType
from email_widget.core.validators import TypeValidator


class ChecklistWidget(BaseWidget):
    """Checklist component for creating task lists and checklists.

    ChecklistWidget is used to display a series of checklist items, each item can have different states (completed, incomplete, skipped, etc.).
    Suitable for task lists, step guides, checklists, and other scenarios.

    Attributes:
        items (List[Dict[str, Any]]): List of checklist items
        title (str): Checklist title
        show_progress (bool): Whether to show progress statistics
        compact_mode (bool): Whether to use compact mode

    Examples:
        Basic usage:
        ```python
        checklist = ChecklistWidget()
        checklist.add_item("Complete Requirements Analysis", True)
        checklist.add_item("Design Database", True)
        checklist.add_item("Write Code", False)
        checklist.add_item("Test Functions", False)
        ```

        Using method chaining:
        ```python
        checklist = (ChecklistWidget()
            .set_title("Project Checklist")
            .add_item("Environment Setup", True)
            .add_item("Code Review", False)
            .show_progress_stats(True))
        ```

        Custom styling:
        ```python
        checklist = ChecklistWidget()
        checklist.add_item("Data Backup", True, "success")
        checklist.add_item("Service Check", False, "warning")
        checklist.add_item("Performance Test", None, "info")  # None means skip
        ```
    """

    TEMPLATE = """
    <div style="
        background: #ffffff;
        border: 1px solid #e1dfdd;
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
    ">
        {% if title %}
        <h3 style="
            color: #323130;
            margin: 0 0 16px 0;
            font-size: 16px;
            font-weight: 600;
        ">{{ title }}</h3>
        {% endif %}
        
        {% if show_progress and items %}
        <div style="
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 16px;
            font-size: 14px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #605e5c; font-weight: 500;">Completion Progress</span>
                <span style="color: #323130; font-weight: 600;">{{ completed_count }}/{{ total_count }} ({{ progress_percentage }}%)</span>
            </div>
            <div style="
                width: 100%;
                height: 8px;
                background: #e1dfdd;
                border-radius: 4px;
                margin-top: 8px;
                overflow: hidden;
            ">
                <div style="
                    width: {{ progress_percentage }}%;
                    height: 100%;
                    background: {{ progress_color }};
                    border-radius: 4px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        {% endif %}

        <div style="{% if compact_mode %}font-size: 13px;{% else %}font-size: 14px;{% endif %}">
            {% for item in items %}
            <div style="
                display: flex;
                align-items: {% if compact_mode %}center{% else %}flex-start{% endif %};
                padding: {% if compact_mode %}6px 0{% else %}8px 0{% endif %};
                {% if not loop.last %}border-bottom: 1px solid #f3f2f1;{% endif %}
                margin-bottom: {% if compact_mode %}4px{% else %}6px{% endif %};
            ">
                <div style="
                    width: 18px;
                    height: 18px;
                    border: 2px solid {{ item.status_color }};
                    border-radius: 3px;
                    margin-right: 12px;
                    margin-top: {% if compact_mode %}0{% else %}2px{% endif %};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: 600;
                    color: {{ item.status_color }};
                    {% if item.is_completed %}background: {{ item.status_color }};{% endif %}
                    flex-shrink: 0;
                ">
                    {{ item.status_icon }}
                </div>
                <div style="flex: 1; line-height: 1.4;">
                    <div style="
                        color: {% if item.is_completed %}#8e8e93{% else %}#323130{% endif %};
                        {% if item.is_completed %}text-decoration: line-through;{% endif %}
                        font-weight: {% if item.is_completed %}400{% else %}500{% endif %};
                        margin-bottom: {% if item.description %}4px{% else %}0{% endif %};
                    ">{{ item.text }}</div>
                    {% if item.description %}
                    <div style="
                        color: #8e8e93;
                        font-size: {% if compact_mode %}11px{% else %}12px{% endif %};
                        line-height: 1.3;
                    ">{{ item.description }}</div>
                    {% endif %}
                </div>
                {% if item.status_text %}
                <div style="
                    color: {{ item.status_color }};
                    font-size: {% if compact_mode %}11px{% else %}12px{% endif %};
                    font-weight: 600;
                    margin-left: 8px;
                ">{{ item.status_text }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
    """

    def __init__(self):
        """Initialize checklist component."""
        super().__init__()
        self._items: list[dict[str, Any]] = []
        self._title: str = ""
        self._show_progress: bool = False
        self._compact_mode: bool = False

        # Initialize validators
        self._str_validator = TypeValidator(str)
        self._bool_validator = TypeValidator(bool)
        self._int_validator = TypeValidator(int)

        # Status theme mapping
        self._status_themes = {
            "success": {"color": "#107c10", "icon": "✓", "text": "Complete"},
            "warning": {"color": "#ff8c00", "icon": "!", "text": "Warning"},
            "error": {"color": "#d13438", "icon": "✗", "text": "Failed"},
            "info": {"color": "#0078d4", "icon": "i", "text": "Info"},
            "primary": {"color": "#0078d4", "icon": "●", "text": "In Progress"},
            "pending": {"color": "#8e8e93", "icon": "○", "text": "Pending"},
            "skipped": {"color": "#8e8e93", "icon": "—", "text": "Skipped"},
        }

    def _get_template_name(self) -> str:
        """Get template name."""
        return "checklist_widget.html"

    def add_item(
        self,
        text: str,
        completed: bool | None = False,
        status_type: str | StatusType | None = None,
        description: str = "",
        status_text: str = "",
    ) -> "ChecklistWidget":
        """Add checklist item.

        Args:
            text (str): Item text content
            completed (Union[bool, None]): Completion status. True=completed, False=incomplete, None=skipped
            status_type (Union[str, StatusType, None]): Status type, see StatusType enum for valid values
            description (str): Item description information
            status_text (str): Custom status text

        Returns:
            ChecklistWidget: Returns self to support method chaining

        Examples:
            ```python
            checklist.add_item("Complete Design", True, "success", "UI design completed")
            checklist.add_item("Code Review", False, "warning", "Awaiting review")
            checklist.add_item("Performance Test", None, "info", "Temporarily skipped")
            ```
        """
        if not self._str_validator.validate(text):
            raise TypeError(
                f"text parameter must be string type, current type: {type(text).__name__}"
            )

        # Determine status
        if completed is True:
            default_status = "success"
        elif completed is False:
            default_status = "pending"
        else:  # None - 跳过状态
            default_status = "skipped"

        # 处理状态类型
        if status_type is None:
            status_key = default_status
        elif isinstance(status_type, StatusType):
            status_key = status_type.value
        else:
            status_key = str(status_type)

        # 验证状态类型
        if status_key not in self._status_themes:
            status_key = default_status

        theme = self._status_themes[status_key]

        # 处理图标显示
        if completed is True:
            icon = "✓" if status_key == "success" else theme["icon"]
            icon_color = "#ffffff" if status_key == "success" else theme["color"]
        else:
            icon = theme["icon"]
            icon_color = theme["color"]

        item = {
            "text": text,
            "description": description,
            "is_completed": completed is True,
            "is_skipped": completed is None,
            "status_color": theme["color"],
            "status_icon": icon,
            "status_text": status_text
            or (theme["text"] if completed is not False else ""),
            "icon_color": icon_color,
        }

        self._items.append(item)
        return self

    def set_title(self, title: str) -> "ChecklistWidget":
        """设置清单标题。

        Args:
            title (str): 清单标题

        Returns:
            ChecklistWidget: 返回self以支持链式调用
        """
        if not self._str_validator.validate(title):
            raise TypeError(
                f"title参数必须是字符串类型，当前类型为: {type(title).__name__}"
            )
        self._title = title
        return self

    def show_progress_stats(self, show: bool = True) -> "ChecklistWidget":
        """设置是否显示进度统计。

        Args:
            show (bool): 是否显示进度条和统计信息

        Returns:
            ChecklistWidget: 返回self以支持链式调用
        """
        if not self._bool_validator.validate(show):
            raise TypeError(
                f"show参数必须是布尔类型，当前类型为: {type(show).__name__}"
            )
        self._show_progress = show
        return self

    def set_compact_mode(self, compact: bool = True) -> "ChecklistWidget":
        """设置紧凑模式。

        Args:
            compact (bool): 是否使用紧凑模式（减少间距和字体大小）

        Returns:
            ChecklistWidget: 返回self以支持链式调用
        """
        if not self._bool_validator.validate(compact):
            raise TypeError(
                f"compact参数必须是布尔类型，当前类型为: {type(compact).__name__}"
            )
        self._compact_mode = compact
        return self

    def clear_items(self) -> "ChecklistWidget":
        """清空所有清单项目。

        Returns:
            ChecklistWidget: 返回self以支持链式调用
        """
        self._items.clear()
        return self

    def remove_item(self, index: int) -> "ChecklistWidget":
        """根据索引移除清单项目。

        Args:
            index (int): 要移除的项目索引

        Returns:
            ChecklistWidget: 返回self以支持链式调用

        Raises:
            IndexError: 当索引超出范围时
        """
        if not self._int_validator.validate(index):
            raise TypeError(
                f"index参数必须是整数类型，当前类型为: {type(index).__name__}"
            )
        if 0 <= index < len(self._items):
            self._items.pop(index)
        else:
            raise IndexError(f"索引 {index} 超出范围，当前有 {len(self._items)} 个项目")
        return self

    def update_item_status(
        self,
        index: int,
        completed: bool | None,
        status_type: str | StatusType | None = None,
    ) -> "ChecklistWidget":
        """更新指定项目的完成状态。

        Args:
            index (int): 项目索引
            completed (Union[bool, None]): 新的完成状态
            status_type (Union[str, StatusType, None]): 可选的状态类型

        Returns:
            ChecklistWidget: 返回self以支持链式调用
        """
        if 0 <= index < len(self._items):
            item = self._items[index]
            text = item["text"]
            description = item.get("description", "")
            status_text = item.get("status_text", "")

            # 移除旧项目并添加更新后的项目
            self._items.pop(index)

            # 重新创建项目（插入到原位置）
            old_items = self._items[:]
            self._items = self._items[:index]
            self.add_item(text, completed, status_type, description, status_text)
            self._items.extend(old_items[index:])

        return self

    @property
    def items(self) -> list[dict[str, Any]]:
        """获取所有清单项目。

        Returns:
            List[Dict[str, Any]]: 清单项目列表
        """
        return self._items.copy()

    @property
    def title(self) -> str:
        """获取清单标题。

        Returns:
            str: 清单标题
        """
        return self._title

    @property
    def item_count(self) -> int:
        """获取清单项目总数。

        Returns:
            int: 项目总数
        """
        return len(self._items)

    @property
    def completed_count(self) -> int:
        """获取已完成项目数量。

        Returns:
            int: 已完成项目数量
        """
        return sum(1 for item in self._items if item["is_completed"])

    @property
    def pending_count(self) -> int:
        """获取待完成项目数量。

        Returns:
            int: 待完成项目数量
        """
        return sum(
            1
            for item in self._items
            if not item["is_completed"] and not item["is_skipped"]
        )

    @property
    def skipped_count(self) -> int:
        """获取跳过项目数量。

        Returns:
            int: 跳过项目数量
        """
        return sum(1 for item in self._items if item["is_skipped"])

    @property
    def completion_percentage(self) -> float:
        """获取完成百分比。

        Returns:
            float: 完成百分比 (0-100)
        """
        if not self._items:
            return 0.0
        # 只计算非跳过项目的完成率
        non_skipped_items = [item for item in self._items if not item["is_skipped"]]
        if not non_skipped_items:
            return 100.0  # 如果所有项目都跳过，认为100%完成
        completed = sum(1 for item in non_skipped_items if item["is_completed"])
        return round((completed / len(non_skipped_items)) * 100, 1)

    def get_template_context(self) -> dict[str, Any]:
        """获取模板渲染上下文。

        Returns:
            Dict[str, Any]: 模板上下文数据
        """
        completed_count = self.completed_count
        total_count = len(
            [item for item in self._items if not item["is_skipped"]]
        )  # 不包含跳过的项目
        progress_percentage = self.completion_percentage

        # 根据完成率确定进度条颜色
        if progress_percentage >= 90:
            progress_color = "#107c10"  # 绿色
        elif progress_percentage >= 70:
            progress_color = "#0078d4"  # 蓝色
        elif progress_percentage >= 50:
            progress_color = "#ff8c00"  # 橙色
        else:
            progress_color = "#8e8e93"  # 灰色

        return {
            "items": self._items,
            "title": self._title,
            "show_progress": self._show_progress,
            "compact_mode": self._compact_mode,
            "completed_count": completed_count,
            "total_count": total_count
            or len(self._items),  # 如果没有非跳过项目，显示总数
            "progress_percentage": progress_percentage,
            "progress_color": progress_color,
        }
