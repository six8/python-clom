from clom.command import Command
from clom import arg

class FabAction(Command):
    """
    Fabric action

    ::

        >>> clom.fab.deploy('dev')
        'fab deploy:dev'


        >>> clom.fab.test('doctest', 'unit').deploy('dev')
        'fab test:doctest,unit deploy:dev'
        
    """

    def _build_action(self, s):
        """
        Encode fab action's parameters in Fabric's format
        """        
        args = []
        for val in self._args:
            if val is not arg.NOTSET:
                args.append(self._escape_arg(val))

        if args:
            s.append('%s:%s' % (
                self._escape_arg(self.name),
                ','.join(args)
            ))
        else:
            s.append(self._escape_arg(self.name))                        

    def _build_args(self, s):
        # Do nothing, we did it in _build_action
        pass
        
    def __getattr__(self, name):
        """
        Get a Fabric action.

        ::

            >>> clom.fab.push
            'fab push'

        """
        parent = self._clone()
        return FabAction(self._clom, name, parent=parent)
                
class FabCommand(Command):
    """
    A command that whose sub-commands are FabActions

    ::

        >>> clom.fab.with_opts('-a', hosts='dev.host').deploy.with_args('dev','test')
        'fab -a --hosts=dev.host deploy:dev,test'

    """
    def __getattr__(self, name):
        """
        Get a Fabric action.

        ::

            >>> clom.fab.push
            'fab push'

        """
        parent = self._clone()
        return FabAction(self._clom, name, parent=parent)
