from typing import List, Optional
from functools import cached_property
from hashlib import md5
import sys

sys.path.append(".")
from src.spider.app.processors.models import ItemTreeNodeData

class ItemNodeChildrenOverflow(BaseException):
    pass

class ItemTreeNodeNotFoundError(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

class ItemTreeNode:
	def __init__(self, key:str, data=None, children=None, parent_node=None, index=None):
		self.key = key
		self.data: Optional[ItemTreeNodeData] = data
		self.index: Optional[List[str]] = index
		self.children = children or []	
		self.parent: Optional[ItemTreeNode] = parent_node
	
	def __str__(self):
		return str({"key": self.key, "data": self.data})

class ItemTree:

	def __init__(self, maxchildren:int=30):
		self.root = ItemTreeNode(key='root')
		self.size = 1
		self.max_children = maxchildren
		self.full = False
		self.cur_node = None

	# @cached_property
	# def full(self):
    
	def find_node(self, node: ItemTreeNode, key):
		if node == None or node.key == key:
			return node		
		for child in node.children:
			return_node = self.find_node(child, key)
			if return_node: 
				return return_node
		return None	

	def add(self, new_key:str, data, parent_node: ItemTreeNode, index: List[str]):
		parent_node = self.root if parent_node == None else parent_node
		new_node = ItemTreeNode(new_key, data, parent_node=parent_node, index=index)
		if len(parent_node.children) < self.max_children:
			parent_node.children.append(new_node)
			self.cur_node = new_node
			self.size += 1
			return new_node
		else: 
			raise ItemNodeChildrenOverflow
	
	def get_branches(self):
		if not self.root:
			return []

		result = []
		stack = [(self.root, [])]

		while stack:
			curr_node, curr_path = stack.pop()
			if not curr_node.children:
				result.append(curr_path + [curr_node.data])
			for child in curr_node.children:
				stack.append((child, curr_path + [curr_node.data]))
		return result

	def get_indexes(self):
		if not self.root:
			return []

		result = []
		stack = [(self.root, [])]

		while stack:
			curr_node, curr_index = stack.pop()
			if not curr_node.children:
				result.append(curr_index + [curr_node.index])
			for child in curr_node.children:
				stack.append((child, curr_index + [curr_node.index]))
		result_indexes = []
		for element in result:
			index = ""
			for index_part in element:
				if index_part:
					index += ''.join(index_part)
			result_indexes.append(md5(index.encode('utf-8')).hexdigest())
		return result_indexes[::-1]

	def get_items(self):
		res = []
		branches = self.get_branches()

		for branch in branches:
			item = dict()
			for element in branch:
				if element:
					item.update(element)
			res.append(item)
		return res[::-1]

	def get_branch_from_cur_node(self):
		cur_node = self.cur_node
		index = self.get_index_from_cur_node()
		res = {}
		while cur_node != self.root:
			res.update(cur_node.data)
			cur_node = cur_node.parent
		res['__hash'] = index
		return res

	def get_index_from_cur_node(self):
		cur_node = self.cur_node
		res = []
		while cur_node != self.root:
			if cur_node.index:
				res += cur_node.index
			cur_node = cur_node.parent
		print(res)
		joined_res = ''.join(res)
		return md5(joined_res.encode('utf-8')).hexdigest()

	def print_tree(self, node: ItemTreeNode, str_aux):
		if node == None: return ""
		str_aux += str(node) + '('
		for i in range(len(node.children)):
			child = node.children[i]
			end = ',' if i < len(node.children) - 1 else ''
			str_aux = self.print_tree(child, str_aux) + end
		str_aux += ')'
		return str_aux

	def is_empty(self):
		return self.size == 0

	def lenght(self):
		return self.size

	def __str__(self):
		return self.print_tree(self.root, "")