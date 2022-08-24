Comments
========

In this example we see several ways to insert Pure Data comments on the patch.


.. code-block:: python
  :linenos:

  import pdpy

  with pdpy.PdPy(name='comments', root=True) as pd:

    comments = pd.createComment(
      "This is a comment",
      "This is yet another one, on the same; object",
      "note that semis and commas are escaped, internally."
    )

    many = 10

    # the function above is a convenience function for the following one
    another = pdpy.Comment("Now we've made " + str(many) + " comments")
    
    for n in range(1,many):
      pd.createComment("we repeated " + str(n) + " times.")
    
    another.addtext('You can add more text to a comment')
    pd.create(another)
    another.addtext('before or after you have created it.')
    
    # for example, the first comment is returned as a list, so 
    comments[0].addtext('neat, right?')
    
    final = pd.createComment("Also, you can have very very long texts and specify  your own breaking point, for example by setting the border property to, say, 250")
    final[0].border = 250


