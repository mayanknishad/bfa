import re

def transform_links(original_text):
	try:
		linked_tokens = re.findall(r'(?<=\<).+?(?=\>)', original_text)
		if len(linked_tokens) > 0:
			transformed_text = original_text
			for link_token in linked_tokens:
				link_text = re.match(r'(.*)\|.*', link_token).group(1)
				anchor_text = re.match(r'.*\|(.*).*', link_token).group(1)
				anchor_text = anchor_text.replace(' ', '_')
				replacment_text = '{0}|{1}'.format(link_text, anchor_text)

				replaced_text = '<{0}>'.format(link_token)
				transformed_text = transformed_text.replace(replaced_text, replacment_text)

			return transformed_text
		else:
			return None
	except:
		return None

