// Clash Verge 地区分组脚本模板
// 将订阅节点按名称中的地区（如"日本"、"香港"、"美国"）拆分为独立代理组
// 注入到主代理组下，方便规则指定地区

function main(config, profileName) {
  const groups = config['proxy-groups'];

  // 提示/公告节点黑名单（不参与地区分组）
  // 根据实际订阅内容调整
  const hintNames = new Set([]);

  // 按地区归类节点名（跳过提示节点）
  const regionMap = {};
  const allProxies = config['proxies'] || [];

  for (const p of allProxies) {
    const name = p.name || '';
    if (hintNames.has(name)) continue;
    // 匹配名称中的中文字符作为地区标识
    const match = name.match(/[\u4e00-\u9fff]+/);
    if (match) {
      const region = match[0];
      if (!regionMap[region]) regionMap[region] = [];
      regionMap[region].push(name);
    }
  }

  // 为标准地区统一创建 url-test 分组
  const regionNames = Object.keys(regionMap).sort();
  const regionGroups = [];

  for (const region of regionNames) {
    const regionKey = `🌍 ${region}`;
    regionGroups.push({
      name: regionKey,
      type: 'url-test',
      proxies: regionMap[region],
      url: 'http://www.gstatic.com/generate_204',
      interval: 86400
    });
  }

  // 找到主代理组（根据实际名称调整）
  const thunderGroup = groups.find(g => g.name === 'Thunder'); // 替换为你的主组名

  // 把地区分组注入到主组的 proxies 列表中
  if (thunderGroup) {
    const regionKeys = regionGroups.map(g => g.name);
    const autoIdx = thunderGroup.proxies.indexOf('自动选择'); // 替换为你的兜底组名
    if (autoIdx >= 0) {
      thunderGroup.proxies.splice(autoIdx, 0, ...regionKeys);
    } else {
      thunderGroup.proxies.unshift(...regionKeys);
    }
  }

  // 把地区分组插入到 proxy-groups 中（在主组后面）
  const thunderIdx = groups.findIndex(g => g.name === 'Thunder');
  if (thunderIdx >= 0) {
    groups.splice(thunderIdx + 1, 0, ...regionGroups);
  } else {
    groups.push(...regionGroups);
  }

  return config;
}
