
class ReprLikeStr:

    def __repr__(self) -> str:
        return self.__str__()


class Tag(ReprLikeStr):

    def __init__(self, text: str, node = None) -> None:
        self.text: str = text
        self.node = node

    @property
    def params(self):
        return self.node.params if self.node else None

    def __str__(self) -> str:
        params = self.params
        if params == None:
            return '[ {} ]'.format(self.text)
        else:
            return '[ {} {} ]'.format(self.text, params)


class Node(ReprLikeStr):

    def __init__(self, parent, tag, tag_end=None) -> None:
        self.parent = parent
        self.level = (parent.level + 1) if parent else 0
        self.children = []
        self.tag = tag
        self.tag_end = tag_end
        self.params = None
        self.text = None

    def __str__(self) -> str:
        pre = '  ' * self.level
        text = self.text if self.text else ''
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
        params_parser = ParamsParser()

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
                params_parser.parse(tag, node)
                tag.node = node
                cur_node.children.append(node)
                if not is_full:
                    cur_node = node
            else:
                if pre_text:
                    cur_node.text = pre_text

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


class ParamsParser:

    def parse(self, tag: Tag, node: Node):
        text = tag.text
        while '  ' in text:
            text = text.replace('  ', ' ')
        lst = text.split(' ')
        tag.text = lst[0]
        params = {}
        for li in lst[1:]:
            if '=' in li:
                lst2 = li.split('=')
                value = lst2[1]
                if value.startswith('"') or value.startswith("'"):
                    value = value[1:-1]
                params[lst2[0]] = value
            else:
                params[li] = True
        if params:
            node.params = params


def noder(path):
    text = open(path, encoding='utf-8').read()

    root = NodeParser().run(text)
    for node in root.children:
        print(node)


if __name__=='__main__':
    noder("example/tst.html")
