import asyncio
import re
from typing import Optional, List
from playwright.async_api import Page, Locator

from commission_setting_mcp.feishu_util import SheetNames
from shared.log_util import log_debug, log_info, log_error
from shared.browser_manager import get_playwright, create_new_tab, is_browser_available


async def is_element_visible(locator: Locator, timeout: int = 5000) -> bool:
    """判断元素是否可见，如果可见返回True，否则返回False，最多等待timeout毫秒
    
    Args:
        locator: Playwright元素定位器
        timeout: 等待超时时间，默认5秒
        
    Returns:
        bool: 元素存在且可见返回True，超时返回False
    """
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        return True
    except Exception as e:
        log_debug(f"等待元素可见超时: {e}")
        return False


async def is_element_enabled(locator: Locator, timeout: int = 5000) -> bool:
    """判断元素是否启用，如果启用返回True，否则返回False，最多等待timeout毫秒
    
    Args:
        locator: Playwright元素定位器
        timeout: 等待超时时间，默认5秒
        
    Returns:
        bool: 元素存在且启用返回True，超时或禁用返回False
    """
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        return await locator.is_enabled()
    except Exception as e:
        log_debug(f"检查元素启用状态失败: {e}")
        return False

def str_start_pattern(title):
    return re.compile(r"^" + title + r".*")


async def open_commission_setting_page(page: Optional[Page] = None) -> tuple[Page, str]:
    """打开聚宝赞商品结算设置页面
    
    Args:
        page: 指定的页面实例，如果为None则使用全局页面实例
        
    Returns:
        tuple[Page, str]: 返回页面实例和操作结果信息
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug(f"open_commission_setting_page: 使用全局页面实例")
    else:
        log_debug(f"open_commission_setting_page: 使用指定页面实例")
    
    # 聚宝赞商品结算设置页面URL
    open_url = "https://m.sesuntech.cn/main_menu/?siteId=12777#%E5%95%86%E5%93%81/%E5%95%86%E5%93%81%E5%BA%93/%E5%95%86%E5%93%81%E7%BB%93%E7%AE%97%E8%AE%BE%E7%BD%AE"
    
    # 打开佣金设置页面
    await page.goto(open_url)

    # await page.pause()
    login_button = page.get_by_role("button", name="登录")
    if await is_element_visible(login_button, timeout=3000):
        return page, "请用户先手动登录，再重新打开原网址进行后续操作！"
    return page, "已打开聚宝赞商品结算设置页面"


async def set_product_commission_plan(product_id: str, page: Optional[Page] = None):
    """设置商品分润方案
    
    Args:
        product_id: 商品ID
        page: 指定的页面实例，如果为None则使用全局页面实例
        
    Returns:
        str: 操作结果信息
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug(f"set_product_commission_plan: 使用全局页面实例")
    else:
        log_debug(f"set_product_commission_plan: 使用指定页面实例")
    
    log_debug(f"set_product_commission_plan for product_id:{product_id}")
    
    # 从飞书表格获取配置
    from commission_setting_mcp.feishu_util import YXXFeishuSheetUtil, SheetName
    feishu_util = YXXFeishuSheetUtil()
    config = await feishu_util.find_by_product_id(SheetNames.REWARD_CONFIG, product_id)
    
    if not config:
        return f"未找到商品{product_id}的配置，配置失败"

    alert_element = page.get_by_role("alert").locator("div").nth(2)
    if await is_element_visible(alert_element, 2000):
        await alert_element.click()

    label_element = page.get_by_label("", exact=True).get_by_role("img")
    # label_element_count = await label_element.count()
    if await is_element_visible(label_element, 2000):
        await label_element.click()
    await page.get_by_role("menuitem", name="商品", exact=True).click()
    await page.get_by_text("商品结算设置").nth(1).click()

    iframe = page.locator("#iframe_active").content_frame
    await iframe.get_by_role("textbox", name="请输入商品ID").click()
    await iframe.get_by_role("textbox", name="请输入商品ID").fill(product_id)
    await iframe.get_by_role("button", name="查询").click()
    await iframe.get_by_text("奖励配置").nth(1).click()
    
    # 等待商品单独设置控件出现
    system_default_radio = iframe.get_by_role("radio", name="商品单独设置")
    
    # 使用封装的等待方法，等待10秒
    if not await is_element_visible(system_default_radio):
        log_error("等待商品单独设置控件超时")
        return '未找到"商品单独设置收益规则"，设置佣金失败'
    

    await system_default_radio.click()
    log_info(f"system_default_radio is selected1: {await system_default_radio.is_checked()}")
    # 检查system_default_radio是否被选中，如果未被选中，等待一秒然后点击，点击完后再次检查，还未选中则重复上述操作，最多循环5次
    await asyncio.sleep(1)
    log_info(f"system_default_radio is selected2: {await system_default_radio.is_checked()}")
    for i in range(5):
        if not await system_default_radio.is_checked():
            await asyncio.sleep(1)
            await system_default_radio.click()
            if i == 4:
                log_error("system_default_radio未被选中，请用户手动处理")
                return f"system_default_radio未被选中，请用户手动处理"
        else:
            break
    
    await iframe.get_by_role("radio", name="否").click()
    
    # 点击分润方式（从config中读取）
    config_name = config.get("分润方式")
    await iframe.get_by_role("radio", name=config_name).first.click()
    
    # 该确定按钮不一定出现，等待一秒，出现就点击，否则跳过
    confirm_button = iframe.get_by_label("切换分佣方式").get_by_role("button", name="确定")
    if await is_element_visible(confirm_button, timeout=1000):
        await confirm_button.click()

    if config_name == "按固定值":
        place_holder_text = "请输入固定值"
    elif config_name == "按比例":
        place_holder_text = "请输入比例"
    else:
        return f"商品{config_name}分润方式不正确，修改后再继续配置"
    # 设置各个等级的固定值
    v1_input = iframe.get_by_role("row", name=str_start_pattern("V1")).get_by_placeholder(place_holder_text).first
    await v1_input.click()
    await v1_input.fill(str(config.get("V1（119/109）", "")))

    v2_input = iframe.get_by_role("row", name=str_start_pattern("V2")).get_by_placeholder(place_holder_text).first
    await v2_input.click()
    await v2_input.fill(str(config.get("V2（99）", "")))

    v3_input = iframe.get_by_role("row", name=str_start_pattern("V3")).get_by_placeholder(place_holder_text).first
    await v3_input.click()
    await v3_input.fill(str(config.get("V3 （89）", "")))

    partner_input = iframe.get_by_role("row", name=str_start_pattern("合作商"), exact=True).get_by_placeholder(place_holder_text).first
    await partner_input.click()
    await partner_input.fill(str(config.get("合作商（82）", "")))

    gold_partner_input = iframe.get_by_role("row", name=str_start_pattern("金牌合作商")).get_by_placeholder(place_holder_text).first
    await gold_partner_input.click()
    await gold_partner_input.fill(str(config.get("金牌合作商（75）", "")))

    diamond_partner_input = iframe.get_by_role("row", name=str_start_pattern("钻石合作商")).get_by_placeholder(place_holder_text).first
    await diamond_partner_input.click()
    await diamond_partner_input.fill(str(config.get("钻石合作商（总教）", "")))
    
    return f"已成功为商品 {product_id} 完成奖励配置，请用户确认后手动点击保存"



async def open_commission_setting_page_in_new_tab() -> tuple[Page, str]:
    """在新标签页中打开聚宝赞商品结算设置页面
    
    Returns:
        tuple[Page, str]: 返回新页面实例和操作结果信息
    """
    # 创建新标签页
    new_page = await create_new_tab()
    log_info("已创建新标签页，准备打开聚宝赞商品结算设置页面")
    
    # 在新标签页中打开页面
    page, result = await open_commission_setting_page(new_page)
    return page, result


async def smart_set_product_commission_plan(product_id: str) -> str:
    """智能设置商品分润方案
    
    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务
    
    Args:
        product_id: 商品ID
        
    Returns:
        str: 操作结果信息
    """
    try:
        log_info(f"智能处理商品 {product_id} 的佣金设置...")
        
        # 检查浏览器是否已经启动
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行任务")
            
            # 在新标签页中打开页面
            page, open_result = await open_commission_setting_page_in_new_tab()
            
            # 如果打开页面失败（比如需要登录），返回结果
            if "请用户先手动登录" in open_result:
                log_error(f"新标签页打开失败: {open_result}")
                return open_result
            
            # 在当前页面设置佣金
            set_result = await set_product_commission_plan(
                product_id, page
            )
            
            log_info(f"新标签页任务完成: {set_result}")
            return f"[新标签页] {set_result}"
            
        else:
            log_info("浏览器未启动，使用传统方式处理")
            
            # 先打开浏览器和页面
            _, open_result = await open_commission_setting_page()
            
            # 如果打开失败，返回结果
            if "请用户先手动登录" in open_result:
                return open_result
            
            # 设置佣金
            set_result = await set_product_commission_plan(product_id)
            
            return f"[首次启动] {set_result}"
            
    except Exception as e:
        error_msg = f"智能设置商品 {product_id} 佣金失败: {str(e)}"
        log_error(error_msg)
        return error_msg


async def open_rebate_set_page(page: Optional[Page] = None) -> tuple[Page, str]:
    """打开服务商返点关联页

    Args:
        page: 指定的页面实例，如果为None则使用全局页面实例

    Returns:
        tuple[Page, str]: 返回页面实例和操作结果信息
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug(f"open_rebate_set_page: 使用全局页面实例")
    else:
        log_debug(f"open_rebate_set_page: 使用指定页面实例")

    # 服务商返点关联页URL
    open_url = "https://m.octochan.cn/facilitator/performance-plan/scheme/rebate-set/index"

    # 打开服务商返点关联页
    await page.goto(open_url)

    # await page.pause()
    login_button = page.get_by_role("button", name="登 录")
    if await is_element_visible(login_button, timeout=3000):
        return page, "请用户先手动登录，再重新打开原网址进行后续操作！"
    return page, "已打开服务商返点关联页"


async def set_product_rebate(product_id: str, profit_sharing_plan: str, page: Optional[Page] = None):
    """设置商品返点

    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
        page: 指定的页面实例，如果为None则使用全局页面实例

    Returns:
        str: 操作结果信息
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug(f"set_product_rebate: 使用全局页面实例")
    else:
        log_debug(f"set_product_rebate: 使用指定页面实例")

    log_debug(f"set_product_rebate for product_id:{product_id}")

    try:
        # 点击服务商返点菜单
        await page.get_by_role("menuitem", name="服务商返点").click()
        # await page.pause()
        # 设置每页显示条数为100条
        page_size_selector = page.locator("#app").get_by_text("条/页")
        await page_size_selector.click()
        await page.get_by_role("option", name="100条/页").click()
        # 等待列表刷新
        await asyncio.sleep(1)

        # 根据profit_sharing_plan动态查找对应的方案行
        target_row = page.get_by_role("row").filter(has_text=profit_sharing_plan)
        if not await is_element_visible(target_row):
            error_msg = f"未找到分润方案 '{profit_sharing_plan}'，请检查方案名称是否正确"
            log_error(error_msg)
            return error_msg
        else:
            log_debug(f"已找到分润方案共'{await target_row.count()}'行")

        # 点击找到的方案行的第一个按钮（关联商品按钮）
        await target_row.get_by_role("button").first.click()
        log_debug(f"已点击方案 '{profit_sharing_plan}' 的关联商品按钮")

        # 点击添加商品按钮
        add_product_button = page.get_by_role("button", name="添加商品")
        if not await is_element_visible(add_product_button):
            log_error("未找到添加商品按钮")
            return f"未找到添加商品按钮，设置商品 {product_id} 返点失败"

        await add_product_button.click()

        # 点击商品名称选项（第二个）
        await page.get_by_label("选择商品").get_by_text("商品名称").nth(1).click()

        # 选择第三方商品ID选项
        third_party_option = page.get_by_role("option", name="第三方商品ID").locator("span")
        if not await is_element_visible(third_party_option):
            log_error("未找到第三方商品ID选项")
            return f"未找到第三方商品ID选项，设置商品 {product_id} 返点失败"

        await third_party_option.click()
        # 点击商品ID输入框并填入商品ID
        product_id_input = page.get_by_role("textbox", name="请输入商品ID")
        if not await is_element_visible(product_id_input):
            log_error("未找到商品ID输入框")
            return f"未找到商品ID输入框，设置商品 {product_id} 返点失败"

        await product_id_input.click()
        await product_id_input.fill(product_id)

        # 点击查询按钮
        search_button = page.get_by_label("选择商品").get_by_role("button", name="查询")
        if not await is_element_visible(search_button):
            log_error("未找到查询按钮")
            return f"未找到查询按钮，设置商品 {product_id} 返点失败"

        await search_button.click()

        # 等待查询结果并点击结果行
        await asyncio.sleep(2)  # 等待查询结果加载
        # await page.pause()
        # 查找包含商品ID的行（使用动态选择器）
        result_row = page.get_by_role("row").filter(has_text=product_id)
        if not await is_element_visible(result_row):
            log_error(f"未找到商品ID {product_id} 的查询结果")
            return f"未找到商品ID {product_id} 的查询结果，请检查商品ID是否正确"

        # 检查并点击查询结果行的选择按钮
        select_button = result_row.locator("span").nth(1)
        
        # 检查元素是否可见和可点击
        if not await is_element_visible(select_button, timeout=2000):
            log_error(f"商品 {product_id} 的选择按钮不可见")
            return f"未找到商品 {product_id} 的选择按钮，设置返点失败"
        
        if await is_element_enabled(select_button, timeout=2000):
            # 元素可见且可点击，执行点击操作
            await select_button.click()
            log_debug(f"已选择商品 {product_id}")
            return f"已成功为商品 {product_id} 设置返点，请用户确认后手动保存"
        else:
            # 元素可见但不可点击，说明商品原来就是选中状态
            log_debug(f"商品 {product_id} 的单选框不可点击，可能已处于选中状态")
            return f"已成功为商品 {product_id} 设置返点，商品原来就是选中状态，请用户确认后手动保存"

    except Exception as e:
        error_msg = f"设置商品 {product_id} 返点失败: {str(e)}"
        log_error(error_msg)
        return error_msg


async def open_rebate_set_page_in_new_tab() -> tuple[Page, str]:
    """在新标签页中打开服务商返点关联页

    Returns:
        tuple[Page, str]: 返回新页面实例和操作结果信息
    """
    # 创建新标签页
    new_page = await create_new_tab()
    log_info("已创建新标签页，准备打开服务商返点关联页")

    # 在新标签页中打开页面
    page, result = await open_rebate_set_page(new_page)
    return page, result


async def smart_set_product_rebate(product_id: str, profit_sharing_plan: str) -> str:
    """智能设置商品返点

    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务

    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称

    Returns:
        str: 操作结果信息
    """
    try:
        log_info(f"智能处理商品 {product_id} 的返点设置...")

        # 检查浏览器是否已经启动
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行任务")

            # 在新标签页中打开页面
            page, open_result = await open_rebate_set_page_in_new_tab()

            # 如果打开页面失败（比如需要登录），返回结果
            if "请用户先手动登录" in open_result:
                log_error(f"新标签页打开失败: {open_result}")
                return open_result

            # 在当前页面设置返点
            set_result = await set_product_rebate(
                product_id, profit_sharing_plan, page
            )

            log_info(f"新标签页任务完成: {set_result}")
            return f"[新标签页] {set_result}"

        else:
            log_info("浏览器未启动，使用传统方式处理")

            # 先打开浏览器和页面
            _, open_result = await open_rebate_set_page()

            # 如果打开失败，返回结果
            if "请用户先手动登录" in open_result:
                return open_result

            # 设置返点
            set_result = await set_product_rebate(product_id, profit_sharing_plan)

            return f"[首次启动] {set_result}"

    except Exception as e:
        error_msg = f"智能设置商品 {product_id} 返点失败: {str(e)}"
        log_error(error_msg)
        return error_msg


async def smart_check_product_commission_setting(product_id: str, profit_sharing_plan: str) -> str:
    """智能检查商品聚宝赞商品分润方案配置和服务商系统商品返点方案配置是否正常

    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务

    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称

    Returns:
        str: 检查结果信息
    """
    try:
        log_info(f"智能检查商品 {product_id} 的分润方案和返点方案配置...")
        
        # 检查聚宝赞商品分润方案配置
        commission_check_result = await _check_commission_setting(product_id, profit_sharing_plan)
        
        # 检查服务商系统返点方案配置
        rebate_check_result = await _check_rebate_setting(product_id, profit_sharing_plan)
        
        # 整合检查结果
        result_lines = []
        result_lines.append(commission_check_result)
        result_lines.append(rebate_check_result)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        error_msg = f"检查商品 {product_id} 配置失败: {str(e)}"
        log_error(error_msg)
        return f"❌ {error_msg}"


async def _check_commission_setting(product_id: str, profit_sharing_plan: str) -> str:
    """检查聚宝赞商品分润方案配置
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
        
    Returns:
        str: 检查结果信息
    """
    try:
        log_info(f"检查商品 {product_id} 的聚宝赞分润方案配置...")
        
        # 智能选择打开方式
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行检查")
            page, open_result = await open_commission_setting_page_in_new_tab()
        else:
            log_info("浏览器未启动，使用传统方式检查")
            page, open_result = await open_commission_setting_page()
        
        # 如果打开页面失败（比如需要登录），返回结果
        if "请用户先手动登录" in open_result:
            log_error(f"打开聚宝赞页面失败: {open_result}")
            return f"❌ 商品 {product_id} 聚宝赞分润方案检查失败：{open_result}"
        
        # 执行页面操作到查询步骤
        alert_element = page.get_by_role("alert").locator("div").nth(2)
        if await is_element_visible(alert_element, 2000):
            await alert_element.click()

        label_element = page.get_by_label("", exact=True).get_by_role("img")
        if await is_element_visible(label_element, 2000):
            await label_element.click()
        
        await page.get_by_role("menuitem", name="商品", exact=True).click()
        await page.get_by_text("商品结算设置").nth(1).click()

        iframe = page.locator("#iframe_active").content_frame
        await iframe.get_by_role("textbox", name="请输入商品ID").click()
        await iframe.get_by_role("textbox", name="请输入商品ID").fill(product_id)
        await iframe.get_by_role("button", name="查询").click()
        
        # 等待查询结果加载
        await asyncio.sleep(2)
        
        # 检查分润方案是否配置正确
        plan_cell = iframe.get_by_role("cell", name=profit_sharing_plan)
        if await is_element_visible(plan_cell, timeout=5000):
            log_info(f"商品 {product_id} 聚宝赞分润方案配置正确")
            return f"✅ 商品 {product_id} 聚宝赞商品分润方案配置正确"
        else:
            # 尝试获取实际配置的方案名称
            try:
                # 查找包含商品ID的行，然后获取其分润方案配置
                await asyncio.sleep(1)
                # 由于无法直接获取具体配置的方案名，返回通用错误信息
                log_error(f"商品 {product_id} 聚宝赞分润方案配置不正确")
                return f"❌ 商品 {product_id} 聚宝赞商品分润方案配置不正确，期望配置：{profit_sharing_plan}"
            except Exception:
                return f"❌ 商品 {product_id} 聚宝赞商品分润方案配置检查异常"
                
    except Exception as e:
        error_msg = f"检查商品 {product_id} 聚宝赞分润方案失败: {str(e)}"
        log_error(error_msg)
        return f"❌ 商品 {product_id} 聚宝赞商品分润方案检查异常：{str(e)}"


async def _check_rebate_setting(product_id: str, profit_sharing_plan: str) -> str:
    """检查服务商系统商品返点方案配置
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 分润方案名称
        
    Returns:
        str: 检查结果信息
    """
    try:
        log_info(f"检查商品 {product_id} 的服务商返点方案配置...")
        
        # 智能选择打开方式
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行检查")
            page, open_result = await open_rebate_set_page_in_new_tab()
        else:
            log_info("浏览器未启动，使用传统方式检查")
            page, open_result = await open_rebate_set_page()
        
        # 如果打开页面失败（比如需要登录），返回结果
        if "请用户先手动登录" in open_result:
            log_error(f"打开服务商页面失败: {open_result}")
            return f"❌ 商品 {product_id} 服务商返点方案检查失败：{open_result}"
        
        # 执行页面操作
        await page.get_by_role("menuitem", name="商品管理").click()
        await page.locator("#app").get_by_text("商品名称").click()
        await page.get_by_role("option", name="第三方商品ID").locator("span").click()
        
        product_id_input = page.get_by_role("textbox", name="请输入商品ID")
        if not await is_element_visible(product_id_input):
            return f"❌ 商品 {product_id} 服务商返点方案检查失败：未找到商品ID输入框"
        
        await product_id_input.click()
        await product_id_input.fill(product_id)
        await page.get_by_role("button", name="查询").click()
        
        # 等待查询结果
        await asyncio.sleep(3)
        
        # 点击奖励设置按钮
        reward_button = page.get_by_role("button", name="奖励设置")
        if not await is_element_visible(reward_button, timeout=5000):
            return f"❌ 商品 {product_id} 服务商返点方案检查失败：未找到商品或奖励设置按钮"
        
        await reward_button.click()
        
        # 等待奖励设置页面加载
        await asyncio.sleep(2)
        
        # 检查关联返点方案单选框是否选中
        rebate_radio = page.locator("label").filter(has_text="关联返点方案").locator("span").nth(1)
        if not await is_element_visible(rebate_radio, timeout=5000):
            return f"❌ 商品 {product_id} 服务商返点方案检查失败：未找到关联返点方案选项"
        
        # 检查单选框是否选中
        is_radio_checked = await rebate_radio.is_checked()
        if not is_radio_checked:
            return f"❌ 商品 {product_id} 服务商系统返点方案配置不正确，未选择关联返点方案"
        
        # 检查返点方案文本是否正确
        rebate_text = page.get_by_label("奖励设置").get_by_text(profit_sharing_plan)
        if await is_element_visible(rebate_text, timeout=3000):
            log_info(f"商品 {product_id} 服务商返点方案配置正确")
            return f"✅ 商品 {product_id} 服务商系统返点方案配置正确"
        else:
            # 尝试获取实际配置的方案名称
            try:
                # 由于无法直接获取文本内容，返回通用错误信息
                log_error(f"商品 {product_id} 服务商返点方案配置不正确")
                return f"❌ 商品 {product_id} 服务商系统返点方案配置不正确，期望配置：{profit_sharing_plan}"
            except Exception:
                return f"❌ 商品 {product_id} 服务商系统返点方案配置检查异常"
                
    except Exception as e:
        error_msg = f"检查商品 {product_id} 服务商返点方案失败: {str(e)}"
        log_error(error_msg)
        return f"❌ 商品 {product_id} 服务商系统返点方案检查异常：{str(e)}"


async def query_promoter_product_id(wechat_product_id: str, page: Optional[Page] = None) -> str:
    """查询推客商品ID
    
    Args:
        wechat_product_id: 微信商品ID
        page: 指定的页面实例，如果为None则使用全局页面实例
        
    Returns:
        str: 推客商品ID，如果不存在则返回 "/"，有异常则返回异常提示
    """
    if page is None:
        _, _, page = await get_playwright()
        log_debug(f"query_promoter_product_id: 使用全局页面实例")
    else:
        log_debug(f"query_promoter_product_id: 使用指定页面实例")
    
    log_info(f"开始查询微信商品ID {wechat_product_id} 对应的推客商品ID...")
    
    try:
        # 智能选择打开方式，参考smart_set_product_commission_plan的实现
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行查询")
            page, open_result = await open_commission_setting_page_in_new_tab()
        else:
            log_info("浏览器未启动，使用传统方式查询")
            page, open_result = await open_commission_setting_page()
        
        # 如果打开页面失败（比如需要登录），返回结果
        if "请用户先手动登录" in open_result:
            log_error(f"打开聚宝赞页面失败: {open_result}")
            return open_result
        
        # 关闭弹层，保持与set_product_commission_plan一致的步骤
        alert_element = page.get_by_role("alert").locator("div").nth(2)
        if await is_element_visible(alert_element, 2000):
            await alert_element.click()

        label_element = page.get_by_label("", exact=True).get_by_role("img")
        if await is_element_visible(label_element, 2000):
            await label_element.click()
        
        # 导航到视频号 -> 推客商品
        await page.get_by_role("menuitem", name="视频号").click()
        await page.get_by_text("推客商品").click()
        
        # 在iframe中进行操作
        iframe = page.locator("#iframe_active").content_frame
        
        # 输入机构商品编码
        product_input = iframe.locator("div").filter(has_text=re.compile(r"^机构商品编码：$")).get_by_placeholder("请输入")
        await product_input.click()
        await product_input.fill(wechat_product_id)
        await iframe.get_by_role("button", name="查询").click()
        
        # 等待查询结果加载
        await asyncio.sleep(2)
        
        # 定义要检查的标签页列表，默认在第一个标签页（已上架）
        tabs_to_check = [
            {"name": "已上架", "element": None},  # 当前默认标签页
            {"name": "已下架", "element": iframe.get_by_role("tab", name="已下架")},
            {"name": "待选品", "element": iframe.get_by_role("tab", name="待选品")}
        ]
        
        # 遍历所有标签页查找商品
        for tab_info in tabs_to_check:
            log_info(f"在 {tab_info['name']} 标签页中查找商品...")
            
            # 如果不是第一个标签页，需要先点击切换
            if tab_info["element"] is not None:
                await tab_info["element"].click()
                await asyncio.sleep(1)  # 等待标签页切换完成
            
            # 检查是否存在显示机构商品编码的控件
            product_code_element = iframe.get_by_text(f"机构商品编码:{wechat_product_id}")
            if await is_element_visible(product_code_element, timeout=2000):
                log_info(f"在 {tab_info['name']} 标签页找到商品编码: {wechat_product_id}")
                
                # 查找ID控件
                id_element = iframe.get_by_text(re.compile(r"^ID:\d+"))
                if await is_element_visible(id_element, timeout=1000):
                    # 提取ID文本
                    id_text = await id_element.text_content()
                    if id_text and id_text.startswith("ID:"):
                        promoter_id = id_text.replace("ID:", "")
                        log_info(f"找到推客商品ID: {promoter_id}")
                        return promoter_id
                else:
                    log_info(f"在 {tab_info['name']} 标签页找到商品但未找到ID控件")
            else:
                log_debug(f"在 {tab_info['name']} 标签页未找到商品编码: {wechat_product_id}")
        
        # 所有标签页都没找到商品
        log_info(f"在所有标签页中都未找到微信商品ID: {wechat_product_id}")
        return "/"
        
    except Exception as e:
        error_msg = f"查询推客商品ID失败: {str(e)}"
        log_error(error_msg)
        return error_msg


async def smart_query_promoter_product_id(wechat_product_ids: List[str]) -> str:
    """智能查询推客商品ID
    
    自动判断浏览器状态：
    - 如果浏览器已打开，在新标签页中执行任务
    - 如果浏览器未打开，先打开浏览器再执行任务
    
    Args:
        wechat_product_ids: 微信商品ID列表
        
    Returns:
        str: 推客商品ID列表（换行符分隔），如果不存在则对应位置返回 "/"
              如果发生异常（如未登录），则只返回一个异常信息
    """
    try:
        log_info(f"智能查询微信商品ID列表 {wechat_product_ids} 对应的推客商品ID...")
        
        page = None
        if is_browser_available():
            log_info("检测到浏览器已启动，在新标签页中执行查询")
            page, open_result = await open_commission_setting_page_in_new_tab()
            if "请用户先手动登录" in open_result:
                log_error(f"新标签页打开失败: {open_result}")
                return open_result
        else:
            log_info("浏览器未启动，使用传统方式查询")
            
        # 批量查询推客商品ID
        results = []
        for wechat_product_id in wechat_product_ids:
            log_info(f"查询商品ID: {wechat_product_id}")
            result = await query_promoter_product_id(wechat_product_id, page)
            
            # 检查是否有异常信息（非 "/" 的异常）
            if result not in ["/"] and ("异常" in result or "失败" in result or "登录" in result):
                log_error(f"查询商品 {wechat_product_id} 时发生异常: {result}")
                return result  # 返回异常信息，不继续处理
            
            results.append(result)
            log_info(f"商品 {wechat_product_id} 查询结果: {result}")
        
        log_info(f"批量查询完成: {results}")
        return "\n".join(results)
            
    except Exception as e:
        error_msg = f"智能查询推客商品ID失败: {str(e)}"
        log_error(error_msg)
        return error_msg