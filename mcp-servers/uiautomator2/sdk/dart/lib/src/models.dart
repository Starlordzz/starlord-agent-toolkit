/// Models and Selectors for Dart Automation Client.

class Selector {
  final String? text;
  final String? textContains;
  final String? textMatches;
  final String? resourceId;
  final String? resourceIdMatches;
  final String? className;
  final String? description;
  final String? descriptionContains;
  final String? xpath;
  final int? index;

  Selector({
    this.text,
    this.textContains,
    this.textMatches,
    this.resourceId,
    this.resourceIdMatches,
    this.className,
    this.description,
    this.descriptionContains,
    this.xpath,
    this.index,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (text != null) map['text'] = text;
    if (textContains != null) map['text_contains'] = textContains;
    if (textMatches != null) map['text_matches'] = textMatches;
    if (resourceId != null) map['resource_id'] = resourceId;
    if (resourceIdMatches != null) map['resource_id_matches'] = resourceIdMatches;
    if (className != null) map['class_name'] = className;
    if (description != null) map['description'] = description;
    if (descriptionContains != null) map['description_contains'] = descriptionContains;
    if (xpath != null) map['xpath'] = xpath;
    if (index != null) map['index'] = index;
    return map;
  }
}

class LLMConfig {
  final String? apiKey;
  final String? baseUrl;
  final String? model;

  LLMConfig({this.apiKey, this.baseUrl, this.model});

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (apiKey != null) map['api_key'] = apiKey;
    if (baseUrl != null) map['base_url'] = baseUrl;
    if (model != null) map['model'] = model;
    return map;
  }
}

