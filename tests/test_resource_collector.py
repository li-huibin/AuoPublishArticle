"""
ResourceCollector 单元测试
测试所有新增和改进的功能
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.resource_collector import ResourceCollector


class TestResourceCollector(unittest.TestCase):
    """ResourceCollector 测试类"""

    def setUp(self):
        """每个测试前的准备工作"""
        self.collector = ResourceCollector()

    def test_generate_search_variants_short_topic(self):
        """测试生成搜索词变体 - 短话题"""
        variants = self.collector._generate_search_variants("AI技术")
        
        self.assertIsInstance(variants, list)
        self.assertGreater(len(variants), 1, "短话题应生成多个变体")
        self.assertIn("AI技术", variants, "原始词应在变体列表中")
        self.assertLessEqual(len(variants), 3, "变体数量不应超过3个")
        
        # 验证没有重复
        self.assertEqual(len(variants), len(set(variants)), "变体列表不应有重复")
        
        print(f"[OK] 短话题变体测试通过: {variants}")

    def test_generate_search_variants_long_topic(self):
        """测试生成搜索词变体 - 长话题"""
        variants = self.collector._generate_search_variants(
            "研究发现全球1700种语言存在神秘规律"
        )
        
        self.assertIsInstance(variants, list)
        self.assertGreaterEqual(len(variants), 1, "长话题至少应有原始词")
        self.assertLessEqual(len(variants), 3, "变体数量不应超过3个")
        
        # 验证提取了更短的版本
        has_shorter = any(len(v) < 20 for v in variants[1:])
        self.assertTrue(has_shorter or len(variants) == 1, "长话题应提取短版本")
        
        print(f"[OK] 长话题变体测试通过: {variants}")

    def test_is_duplicate_by_title(self):
        """测试标题去重功能"""
        item1 = {'title': '测试标题', 'content': '内容1'}
        item2 = {'title': '测试标题', 'content': '内容2'}
        
        # 重置去重集合
        self.collector._seen_titles = set()
        self.collector._seen_content_hashes = set()
        
        # 第一次不应被判定为重复
        is_dup1 = self.collector._is_duplicate(item1)
        self.assertFalse(is_dup1, "第一次出现的标题不应被判定为重复")
        
        # 第二次应被判定为重复
        is_dup2 = self.collector._is_duplicate(item2)
        self.assertTrue(is_dup2, "相同标题应被判定为重复")
        
        print("[OK] 标题去重测试通过")

    def test_is_duplicate_by_content(self):
        """测试内容哈希去重功能"""
        content = "这是一段测试内容" * 10  # 确保内容足够长
        item1 = {'title': '标题1', 'content': content}
        item2 = {'title': '标题2', 'content': content}
        
        # 重置去重集合
        self.collector._seen_titles = set()
        self.collector._seen_content_hashes = set()
        
        # 第一次不应被判定为重复
        is_dup1 = self.collector._is_duplicate(item1)
        self.assertFalse(is_dup1, "第一次出现的内容不应被判定为重复")
        
        # 第二次应被判定为重复（即使标题不同）
        is_dup2 = self.collector._is_duplicate(item2)
        self.assertTrue(is_dup2, "相同内容应被判定为重复")
        
        print("[OK] 内容哈希去重测试通过")

    def test_detect_encoding_from_meta(self):
        """测试从HTML meta标签检测编码"""
        mock_response = Mock()
        mock_response.encoding = 'ISO-8859-1'  # 默认编码，需要检测
        mock_response.text = '<meta charset="utf-8">'
        
        encoding = self.collector._detect_encoding(mock_response)
        self.assertEqual(encoding, 'utf-8', "应从meta标签检测到UTF-8编码")
        
        print("[OK] 编码检测测试通过")

    def test_clean_content(self):
        """测试内容清理功能"""
        dirty_text = """
        这是正文内容。
        扫一扫关注我们
        版权所有
        正文继续...
        微信公众号：xxxxx
        分享到微博
        """
        
        clean_text = self.collector._clean_content(dirty_text)
        
        # 验证垃圾关键词被移除
        self.assertNotIn('扫一扫', clean_text)
        self.assertNotIn('版权所有', clean_text)
        self.assertNotIn('微信公众号', clean_text)
        self.assertNotIn('分享到', clean_text)
        
        # 验证正文内容保留
        self.assertIn('正文内容', clean_text)
        self.assertIn('正文继续', clean_text)
        
        print("[OK] 内容清理测试通过")

    @patch('requests.Session.get')
    def test_search_bing_success(self, mock_get):
        """测试必应搜索成功场景"""
        # Mock 必应搜索结果页面
        mock_response = Mock()
        mock_response.encoding = 'utf-8'
        mock_response.text = """
        <html>
        <body>
        <li class="b_algo">
            <h2><a href="https://example.com/article1">测试标题1</a></h2>
            <div class="b_caption">
                <p>这是测试摘要内容1</p>
            </div>
        </li>
        <li class="b_algo">
            <h2><a href="https://example.com/article2">测试标题2</a></h2>
            <div class="b_caption">
                <p>这是测试摘要内容2</p>
            </div>
        </li>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        results = self.collector._search_bing("测试关键词", max_results=5, fetch_full_text=False)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "应返回搜索结果")
        
        # 验证结果结构
        if results:
            first_result = results[0]
            self.assertIn('source', first_result)
            self.assertEqual(first_result['source'], '必应搜索')
            self.assertIn('title', first_result)
            self.assertIn('url', first_result)
            self.assertIn('content', first_result)
        
        print(f"[OK] 必应搜索测试通过，返回 {len(results)} 条结果")

    @patch('requests.Session.get')
    def test_search_zhihu_via_baidu(self, mock_get):
        """测试通过百度搜索知乎内容"""
        # Mock 百度 site:zhihu.com 搜索结果
        mock_response = Mock()
        mock_response.encoding = 'utf-8'
        mock_response.text = """
        <html>
        <body>
        <div class="result c-container">
            <h3><a href="https://www.zhihu.com/question/123">知乎讨论：测试话题</a></h3>
            <div class="c-abstract">这是知乎上关于测试话题的讨论内容</div>
        </div>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        results = self.collector._search_zhihu("测试话题", max_results=4)
        
        self.assertIsInstance(results, list)
        
        # 验证结果来源标记为知乎
        if results:
            first_result = results[0]
            self.assertEqual(first_result['source'], '知乎')
            self.assertIn('title', first_result)
            self.assertIn('content', first_result)
        
        print(f"[OK] 知乎搜索测试通过，返回 {len(results)} 条结果")

    def test_fetch_full_text_skip_baidu_domains(self):
        """测试跳过百度域名链接"""
        baidu_url = "https://baike.baidu.com/item/test"
        result = self.collector._fetch_full_text(baidu_url)
        
        self.assertEqual(result, '', "应跳过百度百科等域名")
        
        print("[OK] 跳过百度域名测试通过")

    def test_format_resources_with_source_labels(self):
        """测试资料格式化带来源标注"""
        resources = {
            'search_results': [
                {
                    'source': '百度搜索',
                    'title': '测试标题1',
                    'content': '测试内容1',
                    'url': 'http://example.com/1',
                    'full_text': '完整文本内容1' * 50
                },
                {
                    'source': '必应搜索',
                    'title': '测试标题2',
                    'content': '测试内容2',
                    'url': 'http://example.com/2',
                    'full_text': '完整文本内容2' * 50
                }
            ],
            'zhihu_discussions': [
                {
                    'source': '知乎',
                    'title': '知乎讨论',
                    'content': '知乎内容',
                    'url': 'http://zhihu.com/test'
                }
            ]
        }
        
        formatted = self.collector.format_resources_for_prompt(resources)
        
        # 验证包含来源标注
        self.assertIn('[百度搜索]', formatted)
        self.assertIn('[必应搜索]', formatted)
        self.assertIn('知乎社区讨论', formatted)
        
        # 验证包含标题
        self.assertIn('测试标题1', formatted)
        self.assertIn('测试标题2', formatted)
        
        # 验证包含使用规则
        self.assertIn('资料使用规则', formatted)
        
        print("[OK] 资料格式化测试通过")

    def test_check_resource_quality_good(self):
        """测试资料质量检查 - 优质资料"""
        resources = {
            'search_results': [
                {
                    'title': f'标题{i}',
                    'content': '内容' * 100,
                    'full_text': '完整内容' * 100
                }
                for i in range(6)
            ]
        }
        
        quality = self.collector.check_resource_quality(resources)
        
        self.assertTrue(quality['has_valid_data'])
        self.assertEqual(quality['total_count'], 6)
        self.assertEqual(quality['full_text_count'], 6)
        self.assertGreater(quality['quality_score'], 60, "优质资料评分应大于60")
        
        print(f"[OK] 优质资料检查测试通过，评分: {quality['quality_score']}")

    def test_check_resource_quality_poor(self):
        """测试资料质量检查 - 低质资料"""
        resources = {
            'search_results': [
                {
                    'title': '标题',
                    'content': '短',  # 内容太短
                    'full_text': ''  # 无全文
                }
            ]
        }
        
        quality = self.collector.check_resource_quality(resources)
        
        self.assertGreater(len(quality['issues']), 0, "低质资料应有问题提示")
        self.assertLess(quality['quality_score'], 50, "低质资料评分应较低")
        
        print(f"[OK] 低质资料检查测试通过，评分: {quality['quality_score']}, 问题: {quality['issues']}")

    @patch('requests.Session.get')
    def test_collect_resources_integration(self, mock_get):
        """集成测试：完整的资料收集流程"""
        # Mock 多个搜索引擎的响应
        mock_response = Mock()
        mock_response.encoding = 'utf-8'
        mock_response.text = """
        <html>
        <body>
        <div class="result c-container">
            <h3><a href="https://example.com/test">集成测试标题</a></h3>
            <div class="c-abstract">这是集成测试的摘要内容</div>
        </div>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # 执行完整收集流程（关闭全文抓取以加快测试）
        resources = self.collector.collect_resources(
            "测试话题",
            max_results=3,
            fetch_full_text=False
        )
        
        # 验证返回结构
        self.assertIn('search_results', resources)
        self.assertIn('zhihu_discussions', resources)
        self.assertIn('weibo_posts', resources)
        self.assertIn('summary', resources)
        
        print("[OK] 集成测试通过")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行 ResourceCollector 单元测试")
    print("=" * 60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestResourceCollector)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print(f"测试完成: 运行 {result.testsRun} 个测试")
    print(f"[OK] 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"[FAIL] 失败: {len(result.failures)}")
    if result.errors:
        print(f"[ERROR] 错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
