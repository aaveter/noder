
from styler import Style


class ReprLikeStr:

    def __repr__(self) -> str:
        return self.__str__()


class Tag(ReprLikeStr):

    def __init__(self, text: str, node = None) -> None:
        self.text: str = text
        self.node = node

    @property
    def attrs(self):
        return self.node.attrs if self.node else None

    def __str__(self) -> str:
        attrs = self.attrs
        if attrs == None:
            return '[ {} ]'.format(self.text)
        else:
            return '[ {} {} ]'.format(self.text, attrs)


class Node(ReprLikeStr):

    def __init__(self, parent, tag, tag_end=None) -> None:
        self.parent = parent
        self.level = (parent.level + 1) if parent else 0
        self.children = []
        self.tag = tag
        self.tag_end = tag_end
        self.attrs = None
        self.text = None

    def __str__(self) -> str:
        pre = '  ' * self.level
        text = self.text.replace('\n', ' ').strip() if self.text else ''
        if len(text) > 30:
            text = text[:27] + '...'
        s = '{}{}{}'.format(pre, self.tag, text)
        if self.tag_end:
            s += str(self.tag_end)
        lst = [s]
        for node in self.children:
            lst.append(str(node))
        return '\n'.join(lst)


class NodeParser:

    def run(self, text: str):
        pos = 0
        root = cur_node = Node(None, None)
        style = Style()
        attrs_parser = AttrsParser()

        while True:
            i, j, is_start, is_full = self.find_tag(text, pos)
            if i < 0:
                break
            
            pre_text = None
            if i > pos:
                pre_text = text[pos:i]
                if pre_text.isspace():
                    pre_text = None

            tag = Tag(text[i+1:j])
            if is_start:
                if pre_text:
                    p, pend = Tag('p'), Tag('/p')
                    pnode = Node(cur_node, p, pend)
                    p.node = p.pend = pnode
                    pnode.text = pre_text
                    cur_node.children.append(pnode)

                node = Node(cur_node, tag)
                attrs_parser.parse(tag, node)
                style.connect_styles_to_node(node)
                tag.node = node
                cur_node.children.append(node)
                if not is_full:
                    cur_node = node
            else:
                if pre_text:
                    cur_node.text = pre_text
                    if cur_node.tag.text == 'style':
                        style.add_by_text(pre_text)

                cur_node.tag_end = tag
                cur_node = cur_node.parent
            pos = j + 1

        return root

    def find_tag(self, text: str, pos: int):
        i = self.find_tag_start(text, pos)
        if i >= 0:
            j = self.find_tag_end(text, i+1)
            if j >= 0:
                if text[i+1] == '/':
                    return i, j, False, False
                else:
                    if text[j-1] == '/':
                        return i, j, True, True
                    else:
                        return i, j, True, False
        return -1, -1, False, False

    def find_tag_start(self, text, pos):
        return text.find("<", pos)

    def find_tag_end(self, text, pos):
        return text.find(">", pos)


class AttrsParser:

    def parse(self, tag: Tag, node: Node):
        text = tag.text
        while '  ' in text:
            text = text.replace('  ', ' ')

        tag.text = text.split(' ')[0]

        attrs = {}
        lst = text.split('=')
        ln = len(lst)
        for i in range(0, ln-1):
            a, b = lst[i:i+2]
            key = a.split(' ')[-1].strip()
            bb = b.split(' ')
            if i < ln-2:
                bb = bb[:-1]
            value = ' '.join(bb).strip()
            if value.startswith('"') or value.startswith("'"):
                value = value[1:-1]
            if key == 'class':
                attrs['classList'] = [a for a in value.split(' ') if len(a) > 0]
            else:
                attrs[key] = value

        # lst = text.split(' ')
        # tag.text = lst[0]
        # attrs = {}
        # for li in lst[1:]:
        #     if '=' in li:
        #         lst2 = li.split('=')
        #         key, value = lst2[0].strip(), lst2[1].strip()
        #         if value.startswith('"') or value.startswith("'"):
        #             value = value[1:-1]
        #         if key == 'class':
        #             attrs['classList'] = [a for a in value.split(' ') if len(a) > 0]
        #         else:
        #             attrs[key] = value
        #     else:
        #         attrs[li] = True
        if attrs:
            node.attrs = attrs


def noder_parse_file(path):
    text = open(path, encoding='utf-8').read()
    root = NodeParser().run(text)
    return root


def noder(path):
    root = noder_parse_file(path)
    for node in root.children:
        print(node)


if __name__=='__main__':
    noder("example/tst.html")
